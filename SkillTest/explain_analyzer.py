"""PostgreSQL EXPLAIN (ANALYZE, BUFFERS) & SQL Query Diagnosis Engine.

Parses PostgreSQL execution plans (Text or JSON format) and the accompanying SQL query,
computes true inclusive and exclusive (self) execution times accounting for loop counts,
quantifies shared/temp/local buffer I/O in KiB/MiB, correlates predicates and sort/join keys
with the SQL text, and generates concrete DBA actions across three buckets:
1. Index changes (CREATE INDEX CONCURRENTLY ... with covering/partial/functional clauses)
2. Query rewrites (Before -> After SQL transformations)
3. PostgreSQL settings & maintenance (work_mem, ANALYZE, statistics, parallel/cost GUCs)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


BLOCK_SIZE_KB = 8  # Standard PostgreSQL 8 KiB block size


@dataclass
class PlanNode:
    node_id: int
    depth: int
    indent: int
    node_type: str
    raw_header: str
    relation: str | None = None
    alias: str | None = None
    index_name: str | None = None
    scan_direction: str | None = None
    subplan_name: str | None = None
    # Planner estimates
    startup_cost: float = 0.0
    total_cost: float = 0.0
    plan_rows: int = 0
    plan_width: int = 0
    # Runtime actuals (EXPLAIN ANALYZE)
    has_actuals: bool = False
    never_executed: bool = False
    actual_startup_ms: float = 0.0
    actual_total_ms: float = 0.0  # Per-loop inclusive ms reported by Postgres
    actual_rows: int = 0  # Per-loop average rows reported by Postgres
    actual_loops: int = 1
    # Derived timings
    inclusive_ms: float = 0.0  # actual_total_ms * actual_loops
    exclusive_ms: float = 0.0  # inclusive_ms - sum(child.inclusive_ms)
    pct_of_total: float = 0.0
    total_actual_rows: int = 0  # actual_rows * actual_loops
    row_est_factor: float = 1.0  # max(actual/plan, plan/actual)
    row_est_direction: str = "accurate"  # "underestimated", "overestimated", "accurate"
    # Node properties / details
    properties: dict[str, str] = field(default_factory=dict)
    extra_lines: list[str] = field(default_factory=list)
    # Parsed buffer counters (in 8KiB blocks)
    shared_hit: int = 0
    shared_read: int = 0
    shared_dirtied: int = 0
    shared_written: int = 0
    temp_read: int = 0
    temp_written: int = 0
    io_read_time_ms: float = 0.0
    io_write_time_ms: float = 0.0
    # Tree structure
    children: list["PlanNode"] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


_COST_ACTUAL_RE = re.compile(
    r"\(cost=(?P<s_cost>\d+(?:\.\d+)?)\.\.(?P<t_cost>\d+(?:\.\d+)?)\s+"
    r"rows=(?P<p_rows>\d+)\s+width=(?P<p_width>\d+)\)"
    r"(?:\s*\((?:actual\s+time=(?P<a_start>\d+(?:\.\d+)?)\.\.(?P<a_end>\d+(?:\.\d+)?)\s+"
    r"rows=(?P<a_rows>\d+(?:\.\d+)?)\s+loops=(?P<a_loops>\d+)|(?P<never>never\s+executed))\))?",
    re.IGNORECASE,
)

_ACTUAL_ONLY_RE = re.compile(
    r"\((?:actual\s+time=(?P<a_start>\d+(?:\.\d+)?)\.\.(?P<a_end>\d+(?:\.\d+)?)\s+"
    r"rows=(?P<a_rows>\d+(?:\.\d+)?)\s+loops=(?P<a_loops>\d+)|(?P<never>never\s+executed))\)",
    re.IGNORECASE,
)

_HEADER_RELATION_PATTERNS = [
    # Index Scan / Index Only Scan [Backward] using <idx> on <table> [alias]
    re.compile(
        r"^(?P<ntype>Parallel\s+Index\s+Only\s+Scan|Index\s+Only\s+Scan|Parallel\s+Index\s+Scan|Index\s+Scan)"
        r"(?:\s+(?P<dir>Backward|Forward))?\s+using\s+(?P<idx>[^\s]+)\s+on\s+(?P<rel>[^\s]+)"
        r"(?:\s+(?P<alias>[^\s]+))?$",
        re.IGNORECASE,
    ),
    # Bitmap Index Scan on <idx>
    re.compile(
        r"^(?P<ntype>Bitmap\s+Index\s+Scan)\s+on\s+(?P<idx>[^\s]+)$",
        re.IGNORECASE,
    ),
    # Seq Scan / Bitmap Heap Scan / Tid Scan / Subquery Scan / CTE Scan / Function Scan / Foreign Scan / Insert / Update / Delete on <table> [alias]
    re.compile(
        r"^(?P<ntype>(?:Parallel\s+)?(?:Seq\s+Scan|Bitmap\s+Heap\s+Scan|Tid\s+Scan|Subquery\s+Scan|"
        r"CTE\s+Scan|Function\s+Scan|Foreign\s+Scan|Custom\s+Scan|Sample\s+Scan|"
        r"Insert|Update|Delete|Merge))\s+on\s+(?P<rel>[^\s]+)(?:\s+(?P<alias>[^\s]+))?$",
        re.IGNORECASE,
    ),
]


def _parse_header_descriptor(desc: str) -> dict[str, str | None]:
    desc_clean = desc.strip()
    for pat in _HEADER_RELATION_PATTERNS:
        m = pat.match(desc_clean)
        if m:
            gd = m.groupdict()
            alias = gd.get("alias")
            rel = gd.get("rel")
            if alias and alias.lower() == rel.lower():
                alias = None
            return {
                "node_type": gd.get("ntype") or desc_clean,
                "relation": rel,
                "alias": alias,
                "index_name": gd.get("idx"),
                "scan_direction": gd.get("dir"),
            }
    return {
        "node_type": desc_clean,
        "relation": None,
        "alias": None,
        "index_name": None,
        "scan_direction": None,
    }


def _parse_buffers_line(val: str, node: PlanNode) -> None:
    # Example: shared hit=124 read=45890 dirtied=12 written=0, temp read=4120 written=4125
    for scope, metrics in re.findall(r"(shared|local|temp)\s+([^,]+)", val, flags=re.IGNORECASE):
        scope_l = scope.lower()
        for k, v in re.findall(r"(hit|read|dirtied|written)=(\d+)", metrics, flags=re.IGNORECASE):
            num = int(v)
            kl = k.lower()
            if scope_l in ("shared", "local"):
                if kl == "hit":
                    node.shared_hit += num
                elif kl == "read":
                    node.shared_read += num
                elif kl == "dirtied":
                    node.shared_dirtied += num
                elif kl == "written":
                    node.shared_written += num
            elif scope_l == "temp":
                if kl == "read":
                    node.temp_read += num
                elif kl == "written":
                    node.temp_written += num


def _parse_json_explain(raw_text: str) -> tuple[list[PlanNode], dict[str, float]]:
    """Parse EXPLAIN (FORMAT JSON) into our unified PlanNode tree."""
    data = json.loads(raw_text)
    if isinstance(data, list) and data:
        top = data[0]
    elif isinstance(data, dict):
        top = data
    else:
        raise ValueError("Invalid JSON EXPLAIN structure.")

    if "Plan" not in top:
        raise ValueError("JSON object does not contain a top-level 'Plan' key.")

    meta: dict[str, float] = {}
    if "Planning Time" in top:
        meta["planning_time_ms"] = float(top["Planning Time"])
    if "Execution Time" in top:
        meta["execution_time_ms"] = float(top["Execution Time"])

    counter = [0]

    def build_node(jnode: dict[str, Any], depth: int) -> PlanNode:
        counter[0] += 1
        ntype = str(jnode.get("Node Type", "Unknown"))
        if jnode.get("Parallel Aware"):
            if not ntype.lower().startswith("parallel") and ntype in ("Seq Scan", "Hash", "Index Scan", "Index Only Scan", "Bitmap Heap Scan", "Append"):
                ntype = f"Parallel {ntype}"
        rel = jnode.get("Relation Name") or jnode.get("CTE Name")
        alias = jnode.get("Alias")
        if alias == rel:
            alias = None
        idx = jnode.get("Index Name")
        has_actuals = "Actual Total Time" in jnode or "Actual Loops" in jnode
        loops = int(jnode.get("Actual Loops", 1) or 1)
        never_exec = has_actuals and loops == 0

        raw_hdr = ntype
        if idx and rel:
            raw_hdr = f"{ntype} using {idx} on {rel}"
        elif rel:
            raw_hdr = f"{ntype} on {rel}"

        node = PlanNode(
            node_id=counter[0],
            depth=depth,
            indent=depth * 2,
            node_type=ntype,
            raw_header=raw_hdr,
            relation=rel,
            alias=alias,
            index_name=idx,
            scan_direction=jnode.get("Scan Direction"),
            subplan_name=jnode.get("Subplan Name"),
            startup_cost=float(jnode.get("Startup Cost", 0.0)),
            total_cost=float(jnode.get("Total Cost", 0.0)),
            plan_rows=int(jnode.get("Plan Rows", 0)),
            plan_width=int(jnode.get("Plan Width", 0)),
            has_actuals=has_actuals,
            never_executed=never_exec,
            actual_startup_ms=float(jnode.get("Actual Startup Time", 0.0)),
            actual_total_ms=float(jnode.get("Actual Total Time", 0.0)),
            actual_rows=int(round(float(jnode.get("Actual Rows", 0)))),
            actual_loops=max(loops, 1) if not never_exec else 0,
            shared_hit=int(jnode.get("Shared Hit Blocks", 0)),
            shared_read=int(jnode.get("Shared Read Blocks", 0)),
            shared_dirtied=int(jnode.get("Shared Dirtied Blocks", 0)),
            shared_written=int(jnode.get("Shared Written Blocks", 0)),
            temp_read=int(jnode.get("Temp Read Blocks", 0)),
            temp_written=int(jnode.get("Temp Written Blocks", 0)),
            io_read_time_ms=float(jnode.get("I/O Read Time", 0.0)),
            io_write_time_ms=float(jnode.get("I/O Write Time", 0.0)),
        )

        # Populate standard properties
        prop_map = {
            "Filter": "Filter",
            "Rows Removed by Filter": "Rows Removed by Filter",
            "Index Cond": "Index Cond",
            "Recheck Cond": "Recheck Cond",
            "Rows Removed by Index Recheck": "Rows Removed by Index Recheck",
            "Join Filter": "Join Filter",
            "Rows Removed by Join Filter": "Rows Removed by Join Filter",
            "Hash Cond": "Hash Cond",
            "Merge Cond": "Merge Cond",
            "Sort Key": "Sort Key",
            "Sort Method": "Sort Method",
            "Sort Space Used": "Sort Space Used",
            "Sort Space Type": "Sort Space Type",
            "Group Key": "Group Key",
            "Heap Fetches": "Heap Fetches",
            "Workers Planned": "Workers Planned",
            "Workers Launched": "Workers Launched",
        }
        for jk, pk in prop_map.items():
            if jk in jnode:
                val = jnode[jk]
                if isinstance(val, list):
                    val = ", ".join(str(x) for x in val)
                node.properties[pk] = str(val)

        if "Sort Method" in jnode and "Sort Space Used" in jnode:
            stype = jnode.get("Sort Space Type", "Memory")
            sused = jnode.get("Sort Space Used", 0)
            node.properties["Sort Method"] = f"{jnode['Sort Method']}  {stype}: {sused}kB"

        for child_j in jnode.get("Plans", []):
            node.children.append(build_node(child_j, depth + 1))

        return node

    root = build_node(top["Plan"], 0)
    return [root], meta


def parse_explain_text(raw_text: str) -> tuple[list[PlanNode], dict[str, float]]:
    """Parse PostgreSQL Text or JSON EXPLAIN output into a tree of PlanNodes."""
    cleaned = raw_text.strip()
    if not cleaned:
        raise ValueError("EXPLAIN output is empty.")

    # Detect JSON EXPLAIN format
    if cleaned.startswith("[") or cleaned.startswith("{"):
        return _parse_json_explain(cleaned)

    lines = raw_text.splitlines()
    roots: list[PlanNode] = []
    stack: list[PlanNode] = []
    meta: dict[str, float] = {}
    node_counter = 0
    pending_subplan: str | None = None

    for raw_line in lines:
        # Strip psql table borders or quotes if pasted from psql / pgAdmin
        line = raw_line.rstrip()
        if not line:
            continue
        stripped_border = line.strip()
        if stripped_border.startswith("QUERY PLAN") or re.match(r"^[-+]+$", stripped_border):
            continue
        if re.match(r"^\(\d+\s+rows?\)$", stripped_border, flags=re.IGNORECASE):
            continue
        # Remove surrounding quotes if copied from CSV/pgAdmin output
        if len(stripped_border) >= 2 and stripped_border[0] == '"' and stripped_border[-1] == '"':
            line = stripped_border[1:-1].replace('""', '"')

        # Check Planning / Execution / Trigger / JIT footer lines
        m_plan_time = re.match(r"^\s*Planning(?:\s+Time)?:\s*(\d+(?:\.\d+)?)\s*ms", line, re.IGNORECASE)
        if m_plan_time:
            meta["planning_time_ms"] = float(m_plan_time.group(1))
            continue
        m_exec_time = re.match(r"^\s*(?:Execution\s+Time|Total\s+runtime):\s*(\d+(?:\.\d+)?)\s*ms", line, re.IGNORECASE)
        if m_exec_time:
            meta["execution_time_ms"] = float(m_exec_time.group(1))
            continue
        m_jit = re.match(r"^\s*JIT:", line, re.IGNORECASE)
        if m_jit:
            meta["jit_enabled"] = 1.0
            continue

        # Check InitPlan / SubPlan header line
        m_subplan = re.match(r"^(\s*)(InitPlan|SubPlan)\s+(.+)$", line)
        if m_subplan and "(cost=" not in line:
            pending_subplan = f"{m_subplan.group(2)} {m_subplan.group(3).strip()}"
            continue

        # Check if this line is a plan node header (contains (cost=...) or -> with actual time)
        m_cost = _COST_ACTUAL_RE.search(line)
        if m_cost:
            node_counter += 1
            prefix = line[: m_cost.start()].rstrip()
            # Determine indent
            arrow_idx = prefix.find("->")
            if arrow_idx != -1:
                indent = arrow_idx
                desc = prefix[arrow_idx + 2 :].strip()
            else:
                indent = len(prefix) - len(prefix.lstrip())
                desc = prefix.strip()

            parsed_hdr = _parse_header_descriptor(desc)

            # Check if there is a trailing second parenthesized actuals block
            s_cost = float(m_cost.group("s_cost"))
            t_cost = float(m_cost.group("t_cost"))
            p_rows = int(m_cost.group("p_rows"))
            p_width = int(m_cost.group("p_width"))

            has_actuals = False
            never_exec = False
            a_start = 0.0
            a_end = 0.0
            a_rows = 0
            a_loops = 1

            if m_cost.group("a_start") is not None:
                has_actuals = True
                a_start = float(m_cost.group("a_start"))
                a_end = float(m_cost.group("a_end"))
                a_rows = int(round(float(m_cost.group("a_rows"))))
                a_loops = int(m_cost.group("a_loops"))
            elif m_cost.group("never") is not None:
                has_actuals = True
                never_exec = True
                a_loops = 0
            else:
                # Look in remainder of line for (actual time=...) or (never executed)
                rem = line[m_cost.end() :]
                m_act = _ACTUAL_ONLY_RE.search(rem)
                if m_act:
                    has_actuals = True
                    if m_act.group("never"):
                        never_exec = True
                        a_loops = 0
                    else:
                        a_start = float(m_act.group("a_start"))
                        a_end = float(m_act.group("a_end"))
                        a_rows = int(round(float(m_act.group("a_rows"))))
                        a_loops = int(m_act.group("a_loops"))

            # Determine tree parent from stack by indent
            while stack and stack[-1].indent >= indent:
                stack.pop()
            depth = len(stack)

            node = PlanNode(
                node_id=node_counter,
                depth=depth,
                indent=indent,
                node_type=str(parsed_hdr["node_type"]),
                raw_header=desc,
                relation=parsed_hdr["relation"],
                alias=parsed_hdr["alias"],
                index_name=parsed_hdr["index_name"],
                scan_direction=parsed_hdr["scan_direction"],
                subplan_name=pending_subplan,
                startup_cost=s_cost,
                total_cost=t_cost,
                plan_rows=p_rows,
                plan_width=p_width,
                has_actuals=has_actuals,
                never_executed=never_exec,
                actual_startup_ms=a_start,
                actual_total_ms=a_end,
                actual_rows=a_rows,
                actual_loops=a_loops,
            )
            pending_subplan = None

            if stack:
                stack[-1].children.append(node)
            else:
                roots.append(node)
            stack.append(node)
            continue

        # Otherwise, if we have a current node on the stack, attach property lines
        if stack:
            cur = stack[-1]
            prop_line = line.strip()
            if prop_line.startswith("Buffers:"):
                bval = prop_line[len("Buffers:") :].strip()
                cur.properties["Buffers"] = bval
                _parse_buffers_line(bval, cur)
            elif prop_line.startswith("I/O Timings:"):
                ival = prop_line[len("I/O Timings:") :].strip()
                cur.properties["I/O Timings"] = ival
                m_r = re.search(r"read=(\d+(?:\.\d+)?)", ival, re.IGNORECASE)
                m_w = re.search(r"write=(\d+(?:\.\d+)?)", ival, re.IGNORECASE)
                if m_r:
                    cur.io_read_time_ms += float(m_r.group(1))
                if m_w:
                    cur.io_write_time_ms += float(m_w.group(1))
            elif ":" in prop_line and not prop_line.startswith("->"):
                k, v = prop_line.split(":", 1)
                k_clean = k.strip()
                v_clean = v.strip()
                if k_clean in cur.properties:
                    cur.properties[k_clean] += f"; {v_clean}"
                else:
                    cur.properties[k_clean] = v_clean
            else:
                cur.extra_lines.append(prop_line)

    if not roots:
        raise ValueError(
            "Could not find any PostgreSQL EXPLAIN plan nodes. Make sure your paste includes lines like "
            "'Seq Scan on ... (cost=0.00..10.00 rows=100 width=32) (actual time=...)' or JSON EXPLAIN output."
        )

    return roots, meta


def _compute_node_metrics(roots: list[PlanNode], meta: dict[str, float]) -> tuple[list[PlanNode], float]:
    """Compute inclusive_ms, exclusive_ms, row estimation errors, and flatten nodes."""
    all_nodes: list[PlanNode] = []

    def visit(node: PlanNode) -> float:
        all_nodes.append(node)
        if node.never_executed:
            node.inclusive_ms = 0.0
            node.total_actual_rows = 0
        elif node.has_actuals:
            # In PostgreSQL EXPLAIN ANALYZE, actual_total_ms is per-loop average.
            # Note: for Parallel nodes underneath a Gather, loops = 1 + workers, and actual_total_ms * loops
            # can slightly exceed wall-clock parent Gather time. We clamp exclusive_ms at 0.0.
            loops = max(node.actual_loops, 1)
            node.inclusive_ms = round(node.actual_total_ms * loops, 3)
            node.total_actual_rows = int(node.actual_rows * loops)
        else:
            # Cost-only EXPLAIN fallback: use total_cost as relative proxy
            node.inclusive_ms = round(node.total_cost, 3)
            node.total_actual_rows = node.plan_rows

        children_sum = 0.0
        for ch in node.children:
            ch_inc = visit(ch)
            # If this node is Gather / Gather Merge and child is parallel, child inclusive time is summed across workers;
            # normalize by child.actual_loops so parent exclusive time isn't artificially zeroed out, and scale child inclusive_ms
            # to wall-clock contribution when comparing against query total.
            if "gather" in node.node_type.lower() and ch.actual_loops > 1 and node.actual_loops == 1:
                # Convert parallel worker aggregate time to approximate wall-clock time
                ch_wall = round(ch.inclusive_ms / ch.actual_loops, 3)
                ch.exclusive_ms = round(ch.exclusive_ms / ch.actual_loops, 3)
                ch.inclusive_ms = ch_wall
                children_sum += ch_wall
            else:
                children_sum += ch_inc

        if node.never_executed:
            node.exclusive_ms = 0.0
        elif node.has_actuals:
            node.exclusive_ms = round(max(0.0, node.inclusive_ms - children_sum), 3)
        else:
            child_cost_sum = sum(c.total_cost for c in node.children)
            node.exclusive_ms = round(max(0.0, node.total_cost - child_cost_sum), 3)

        # Row estimate accuracy
        if node.has_actuals and not node.never_executed:
            # Compare per-loop actual_rows vs plan_rows (Postgres plan_rows is per-loop estimate)
            est = max(node.plan_rows, 1)
            act = max(node.actual_rows, 1)
            if act >= est:
                node.row_est_factor = round(act / est, 1)
                node.row_est_direction = "underestimated" if node.row_est_factor >= 5.0 else "accurate"
            else:
                node.row_est_factor = round(est / act, 1)
                node.row_est_direction = "overestimated" if node.row_est_factor >= 5.0 else "accurate"

        return node.inclusive_ms

    for r in roots:
        visit(r)

    total_time = meta.get("execution_time_ms", 0.0)
    if total_time <= 0.0 and roots:
        total_time = max(r.inclusive_ms for r in roots)
    if total_time <= 0.0:
        total_time = sum(n.exclusive_ms for n in all_nodes) or 1.0

    for n in all_nodes:
        n.pct_of_total = round(min(100.0, (n.exclusive_ms / total_time) * 100.0), 1) if total_time > 0 else 0.0

    return all_nodes, round(total_time, 3)


def _extract_sql_context(sql_text: str) -> dict[str, Any]:
    """Parse table aliases, SELECT columns, WHERE predicates, JOINs, ORDER BY, LIMIT/OFFSET from the SQL query."""
    sql_clean = (sql_text or "").strip()
    if not sql_clean:
        return {
            "has_sql": False,
            "select_star": False,
            "aliases": {},
            "select_cols_by_alias": {},
            "has_not_in": False,
            "has_or_in_where": False,
            "offset_val": None,
            "limit_val": None,
            "order_by_cols": [],
            "leading_wildcard_like": [],
            "function_wrapped_cols": [],
            "correlated_subqueries": [],
        }

    # Normalize comments and whitespace
    no_comments = re.sub(r"--[^\n]*", " ", sql_clean)
    no_comments = re.sub(r"/\*.*?\*/", " ", no_comments, flags=re.DOTALL)
    flat = re.sub(r"\s+", " ", no_comments).strip()

    # Table & alias map: FROM/JOIN <table> [AS] <alias>
    aliases: dict[str, str] = {}
    reserved = {
        "where", "join", "inner", "left", "right", "full", "cross", "on", "group",
        "order", "limit", "offset", "having", "union", "lateral", "select", "set", "values",
    }
    for m in re.finditer(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][\w\.]*)(?:\s+AS\s+([a-zA-Z_]\w*)|\s+([a-zA-Z_]\w*))?",
        flat,
        flags=re.IGNORECASE,
    ):
        tbl = m.group(1).split(".")[-1]
        al = m.group(2) or m.group(3)
        if al and al.lower() not in reserved:
            aliases[al] = tbl
        aliases[tbl] = tbl

    select_star = bool(re.search(r"\bSELECT\s+(?:DISTINCT\s+)?\*", flat, flags=re.IGNORECASE))

    # Extract columns referenced in SELECT list for covering index INCLUDE suggestions
    select_cols_by_alias: dict[str, list[str]] = {}
    m_sel = re.search(r"\bSELECT\s+(.*?)\s+\bFROM\b", flat, flags=re.IGNORECASE)
    if m_sel and not select_star:
        sel_body = m_sel.group(1)
        for m_col in re.finditer(r"\b([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)\b", sel_body):
            al, col = m_col.group(1), m_col.group(2)
            select_cols_by_alias.setdefault(al, [])
            if col not in select_cols_by_alias[al]:
                select_cols_by_alias[al].append(col)
        # Also bare columns if single table
        if len(set(aliases.values())) == 1:
            only_tbl = next(iter(set(aliases.values())))
            for tok in sel_body.split(","):
                tok_c = tok.strip()
                m_bare = re.match(r"^([a-zA-Z_]\w*)(?:\s+AS\s+\w+)?$", tok_c, flags=re.IGNORECASE)
                if m_bare:
                    c = m_bare.group(1)
                    if c.lower() not in ("distinct", "count", "sum", "avg", "min", "max"):
                        select_cols_by_alias.setdefault(only_tbl, [])
                        if c not in select_cols_by_alias[only_tbl]:
                            select_cols_by_alias[only_tbl].append(c)

    has_not_in = bool(re.search(r"\bNOT\s+IN\s*\(\s*SELECT\b", flat, flags=re.IGNORECASE))
    has_or_in_where = bool(re.search(r"\bWHERE\b.*?\bOR\b", flat, flags=re.IGNORECASE))

    m_offset = re.search(r"\bOFFSET\s+(\d+)\b", flat, flags=re.IGNORECASE)
    offset_val = int(m_offset.group(1)) if m_offset else None
    m_limit = re.search(r"\bLIMIT\s+(\d+)\b", flat, flags=re.IGNORECASE)
    limit_val = int(m_limit.group(1)) if m_limit else None

    order_by_cols: list[str] = []
    m_ord = re.search(
        r"\bORDER\s+BY\s+([^;]+?)(?:\s+\bLIMIT\b|\s+\bOFFSET\b|\s+\bFETCH\b|\)|$)",
        flat,
        flags=re.IGNORECASE,
    )
    if m_ord:
        for part in m_ord.group(1).split(","):
            p = part.strip()
            if p:
                order_by_cols.append(p)

    # Leading wildcard LIKE / ILIKE '%...'
    leading_wildcard_like: list[str] = []
    for m_like in re.finditer(
        r"([a-zA-Z_][\w\.]*)\s+(I?LIKE)\s+'%([^']+)'",
        flat,
        flags=re.IGNORECASE,
    ):
        leading_wildcard_like.append(f"{m_like.group(1)} {m_like.group(2).upper()} '%{m_like.group(3)}'")

    # Non-sargable function calls on columns in WHERE: DATE(col), EXTRACT(... FROM col), LOWER(col), UPPER(col), COALESCE(col, ...)
    function_wrapped_cols: list[dict[str, str]] = []
    for m_fn in re.finditer(
        r"\b(LOWER|UPPER|DATE|DATE_TRUNC|EXTRACT|COALESCE|CAST|TO_CHAR)\s*\(\s*(?:[a-zA-Z_]+\s+FROM\s+)?([a-zA-Z_][\w\.]*)",
        flat,
        flags=re.IGNORECASE,
    ):
        fn_name = m_fn.group(1).upper()
        col_ref = m_fn.group(2)
        if col_ref.upper() not in ("YEAR", "MONTH", "DAY", "EPOCH", "HOUR", "NOW", "CURRENT_DATE"):
            function_wrapped_cols.append({"func": fn_name, "column": col_ref, "expr": m_fn.group(0)})

    return {
        "has_sql": True,
        "raw_sql": sql_clean,
        "flat_sql": flat,
        "select_star": select_star,
        "aliases": aliases,
        "select_cols_by_alias": select_cols_by_alias,
        "has_not_in": has_not_in,
        "has_or_in_where": has_or_in_where,
        "offset_val": offset_val,
        "limit_val": limit_val,
        "order_by_cols": order_by_cols,
        "leading_wildcard_like": leading_wildcard_like,
        "function_wrapped_cols": function_wrapped_cols,
    }


_NON_COLUMN_TOKENS = {
    "and", "or", "not", "null", "is", "in", "any", "all", "array", "true", "false",
    "like", "ilike", "between", "case", "when", "then", "else", "end", "numeric",
    "text", "varchar", "integer", "int", "bigint", "date", "timestamp", "timestamptz",
    "interval", "lower", "upper", "date_trunc", "extract", "coalesce", "to_char",
}


def _extract_filter_columns(expr: str, table_name: str | None = None, alias: str | None = None) -> dict[str, Any]:
    """Parse PostgreSQL Filter / Index Cond / Hash Cond expressions into equality, range, and functional columns."""
    if not expr:
        return {"eq_cols": [], "range_cols": [], "func_exprs": [], "has_leading_wildcard": False, "has_or": False}

    # Remove PostgreSQL type casts like ::text, ::numeric, ::timestamp without time zone
    cleaned = re.sub(r"::[a-zA-Z_][\w\s]*?(?=[\)\,\s=<>!]|$)", "", expr)
    # Unwrap single-column parens produced by cast formatting, e.g. (status) -> status
    cleaned = re.sub(r"\(\s*([a-zA-Z_][\w\.]*)\s*\)", r"\1", cleaned)

    has_or = bool(re.search(r"\bOR\b", cleaned, flags=re.IGNORECASE))
    has_leading_wildcard = bool(re.search(r"(?:~~\*?|I?LIKE)\s*'%[^']*'", cleaned, flags=re.IGNORECASE))

    func_exprs: list[str] = []
    for m_fn in re.finditer(
        r"\b(lower|upper|date_trunc|date|coalesce)\s*\((?:[^,\(\)]+,\s*)?([a-zA-Z_][\w\.]*)\s*\)",
        cleaned,
        flags=re.IGNORECASE,
    ):
        fn = m_fn.group(1).lower()
        col = m_fn.group(2).split(".")[-1]
        if col.lower() not in _NON_COLUMN_TOKENS:
            fe = f"{fn}({col})"
            if fe not in func_exprs:
                func_exprs.append(fe)

    eq_cols: list[str] = []
    range_cols: list[str] = []

    # Match comparisons: col = val, col >= val, col < val, col = ANY(...)
    for m_cmp in re.finditer(
        r"\b([a-zA-Z_][\w\.]*)\s*(=|>=|<=|>|<|<>|!=|\s+IS\s+NULL)\s*",
        cleaned,
        flags=re.IGNORECASE,
    ):
        raw_col = m_cmp.group(1)
        op = m_cmp.group(2).strip().upper()
        parts = raw_col.split(".")
        if len(parts) == 2:
            prefix, col = parts[0], parts[1]
            # If table_name or alias is specified, ignore columns belonging to a different table
            if table_name and alias and prefix.lower() not in (table_name.lower(), alias.lower()):
                continue
        else:
            col = parts[-1]

        if col.lower() in _NON_COLUMN_TOKENS or col.isdigit():
            continue

        if op in ("=", "IS NULL"):
            if col not in eq_cols and col not in range_cols:
                eq_cols.append(col)
        elif op in (">=", "<=", ">", "<"):
            if col not in range_cols and col not in eq_cols:
                range_cols.append(col)

    return {
        "eq_cols": eq_cols,
        "range_cols": range_cols,
        "func_exprs": func_exprs,
        "has_leading_wildcard": has_leading_wildcard,
        "has_or": has_or,
        "cleaned_expr": cleaned,
    }


def _serialize_tree(node: PlanNode) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "depth": node.depth,
        "node_type": node.node_type,
        "raw_header": node.raw_header,
        "relation": node.relation,
        "alias": node.alias,
        "index_name": node.index_name,
        "subplan_name": node.subplan_name,
        "startup_cost": node.startup_cost,
        "total_cost": node.total_cost,
        "plan_rows": node.plan_rows,
        "plan_width": node.plan_width,
        "has_actuals": node.has_actuals,
        "never_executed": node.never_executed,
        "actual_startup_ms": node.actual_startup_ms,
        "actual_total_ms": node.actual_total_ms,
        "actual_rows": node.actual_rows,
        "actual_loops": node.actual_loops,
        "inclusive_ms": node.inclusive_ms,
        "exclusive_ms": node.exclusive_ms,
        "pct_of_total": node.pct_of_total,
        "total_actual_rows": node.total_actual_rows,
        "row_est_factor": node.row_est_factor,
        "row_est_direction": node.row_est_direction,
        "properties": node.properties,
        "shared_hit": node.shared_hit,
        "shared_read": node.shared_read,
        "shared_dirtied": node.shared_dirtied,
        "shared_written": node.shared_written,
        "temp_read": node.temp_read,
        "temp_written": node.temp_written,
        "warnings": node.warnings,
        "children": [_serialize_tree(c) for c in node.children],
    }


def _clean_sort_cols(sort_key_str: str, table_name: str | None = None, alias: str | None = None) -> list[str]:
    cols: list[str] = []
    if not sort_key_str:
        return cols
    cleaned = re.sub(r"::[a-zA-Z_][\w\s]*", "", sort_key_str)
    for part in cleaned.split(","):
        tok = part.strip()
        m = re.match(r"^([a-zA-Z_][\w\.]*)(?:\s+(DESC|ASC))?(?:\s+NULLS\s+(?:FIRST|LAST))?$", tok, flags=re.IGNORECASE)
        if m:
            raw_c = m.group(1)
            dir_s = (m.group(2) or "").upper()
            c_parts = raw_c.split(".")
            if len(c_parts) == 2 and table_name and alias:
                if c_parts[0].lower() not in (table_name.lower(), alias.lower()):
                    continue
            col_name = c_parts[-1]
            if col_name.lower() not in _NON_COLUMN_TOKENS:
                cols.append(f"{col_name} {dir_s}".strip())
    return cols


def analyze_explain_and_query(explain_text: str, sql_text: str = "") -> dict[str, Any]:
    """Full PostgreSQL EXPLAIN (ANALYZE) + SQL Query diagnosis."""
    roots, meta = parse_explain_text(explain_text)
    all_nodes, total_time_ms = _compute_node_metrics(roots, meta)
    sql_ctx = _extract_sql_context(sql_text)

    has_any_actuals = any(n.has_actuals for n in all_nodes)
    planning_time_ms = round(meta.get("planning_time_ms", 0.0), 3)

    # Root buffers (or max across nodes if root didn't print aggregate buffers)
    total_shared_hit = max((r.shared_hit for r in roots), default=0) or sum(n.shared_hit for n in all_nodes if not n.children)
    total_shared_read = max((r.shared_read for r in roots), default=0) or sum(n.shared_read for n in all_nodes if not n.children)
    total_temp_read = max((r.temp_read for r in roots), default=0) or max((n.temp_read for n in all_nodes), default=0)
    total_temp_written = max((r.temp_written for r in roots), default=0) or max((n.temp_written for n in all_nodes), default=0)

    total_blocks = total_shared_hit + total_shared_read
    cache_hit_ratio = round((total_shared_hit / total_blocks) * 100.0, 2) if total_blocks > 0 else None
    shared_read_mb = round((total_shared_read * BLOCK_SIZE_KB) / 1024.0, 2)
    shared_hit_mb = round((total_shared_hit * BLOCK_SIZE_KB) / 1024.0, 2)
    temp_spill_mb = round((max(total_temp_written, total_temp_read) * BLOCK_SIZE_KB) / 1024.0, 2)

    findings: list[dict[str, Any]] = []
    index_changes: list[dict[str, Any]] = []
    query_rewrites: list[dict[str, Any]] = []
    setting_changes: list[dict[str, Any]] = []
    seen_index_ddl: set[str] = set()
    seen_settings: set[str] = set()
    seen_rewrites: set[str] = set()

    # Map parent relations and sort keys for index combining (e.g. Sort over Seq Scan)
    parent_map: dict[int, PlanNode] = {}
    for n in all_nodes:
        for ch in n.children:
            parent_map[ch.node_id] = n

    def find_ancestor_sort_cols(node: PlanNode) -> list[str]:
        cur_id = node.node_id
        while cur_id in parent_map:
            par = parent_map[cur_id]
            if "Sort Key" in par.properties:
                sc = _clean_sort_cols(par.properties["Sort Key"], node.relation, node.alias)
                if sc:
                    return sc
            cur_id = par.node_id
        return []

    def find_parent_join_cols(node: PlanNode) -> list[str]:
        cur_id = node.node_id
        while cur_id in parent_map:
            par = parent_map[cur_id]
            for k in ("Hash Cond", "Merge Cond", "Join Filter"):
                if k in par.properties:
                    finfo = _extract_filter_columns(par.properties[k], node.relation, node.alias)
                    if finfo["eq_cols"]:
                        return finfo["eq_cols"]
            cur_id = par.node_id
        return []

    # Evaluate every node for performance bottlenecks
    for node in sorted(all_nodes, key=lambda x: x.exclusive_ms, reverse=True):
        ntype_l = node.node_type.lower()
        rel = node.relation or (sql_ctx["aliases"].get(node.alias or "", None)) or "target_table"
        props = node.properties

        rows_removed_filter = int(re.sub(r"[^\d]", "", props.get("Rows Removed by Filter", "0")) or 0) * max(node.actual_loops, 1)
        rows_removed_recheck = int(re.sub(r"[^\d]", "", props.get("Rows Removed by Index Recheck", "0")) or 0) * max(node.actual_loops, 1)
        rows_removed_join = int(re.sub(r"[^\d]", "", props.get("Rows Removed by Join Filter", "0")) or 0) * max(node.actual_loops, 1)
        heap_fetches = int(re.sub(r"[^\d]", "", props.get("Heap Fetches", "0")) or 0)

        # 1. Sequential Scan with high filtering, high cost, or repeated loops
        if "seq scan" in ntype_l:
            filter_expr = props.get("Filter", "")
            finfo = _extract_filter_columns(filter_expr, node.relation, node.alias)
            sort_cols = find_ancestor_sort_cols(node)
            join_cols = find_parent_join_cols(node)

            total_scanned = node.total_actual_rows + rows_removed_filter
            discard_pct = round((rows_removed_filter / total_scanned) * 100.0, 1) if total_scanned > 0 else 0.0

            is_slow_seq = (
                (node.has_actuals and (node.exclusive_ms >= 5.0 or rows_removed_filter >= 1000 or node.actual_loops > 1))
                or (not node.has_actuals and node.total_cost >= 100.0)
            )
            if is_slow_seq:
                why_parts: list[str] = []
                if node.actual_loops > 1:
                    why_parts.append(
                        f"Executed {node.actual_loops:,} times inside a loop, scanning {total_scanned:,} total rows across iterations"
                    )
                elif rows_removed_filter > 0:
                    why_parts.append(
                        f"Scanned {total_scanned:,} rows on `{rel}` and discarded {rows_removed_filter:,} rows ({discard_pct}%) via CPU filter `{filter_expr}`"
                    )
                else:
                    why_parts.append(f"Full table scan on `{rel}` returning {node.total_actual_rows:,} rows")

                if node.shared_read > 0:
                    read_mb = round((node.shared_read * BLOCK_SIZE_KB) / 1024.0, 2)
                    why_parts.append(f"pulled {node.shared_read:,} blocks ({read_mb} MiB) from storage/OS page cache")

                warn_msg = "; ".join(why_parts) + "."
                node.warnings.append(warn_msg)

                findings.append({
                    "severity": "critical" if (node.pct_of_total >= 35.0 or node.exclusive_ms >= 50.0 or node.actual_loops > 5) else "warning",
                    "node_id": node.node_id,
                    "title": f"{node.node_type} on `{rel}`" + (f" (x{node.actual_loops:,} loops)" if node.actual_loops > 1 else ""),
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.raw_header}` took {node.exclusive_ms:.2f} ms self time ({node.pct_of_total}% of query time).",
                    "why": warn_msg,
                })

                # Build concrete Index recommendation
                if finfo["has_leading_wildcard"]:
                    col_m = re.search(
                        r"([a-zA-Z_]\w*)\s*(?:I?LIKE|~~\*?)\s*'%([^']+)'",
                        finfo.get("cleaned_expr", filter_expr),
                        re.IGNORECASE,
                    )
                    tcol = col_m.group(1) if col_m else (finfo["eq_cols"][0] if finfo["eq_cols"] else "search_col")
                    ddl = (
                        f"CREATE EXTENSION IF NOT EXISTS pg_trgm;\n"
                        f"CREATE INDEX CONCURRENTLY idx_{rel}_{tcol}_trgm\n"
                        f"    ON {rel} USING gin ({tcol} gin_trgm_ops);"
                    )
                    if ddl not in seen_index_ddl:
                        seen_index_ddl.add(ddl)
                        index_changes.append({
                            "table": rel,
                            "type": "GIN Trigram Index (Leading Wildcard LIKE/ILIKE)",
                            "ddl": ddl,
                            "why": f"Standard B-Tree indexes cannot accelerate a leading-wildcard pattern (`{filter_expr}`). A `pg_trgm` GIN index splits strings into 3-character trigrams so PostgreSQL can use a Bitmap Index Scan.",
                            "verify_sql": f"EXPLAIN (ANALYZE, BUFFERS) {sql_text.strip() or f'SELECT * FROM {rel} WHERE {tcol} ILIKE ...;'}",
                        })
                else:
                    # Standard B-Tree index composition: Equality columns -> Sort or Range columns + INCLUDE covering columns
                    idx_cols: list[str] = []
                    clean_funcs = [
                        re.sub(r"^date(?:_trunc)?\((.*)\)$", r"\1", f) if f.startswith(("date(", "date_trunc(")) else f
                        for f in finfo["func_exprs"]
                    ]
                    for c in join_cols + finfo["eq_cols"] + clean_funcs:
                        if c not in idx_cols:
                            idx_cols.append(c)
                    # Add sort columns or range columns (B-Tree rule: equality first, then sort/range)
                    for sc in sort_cols:
                        sc_base = sc.split()[0]
                        if sc_base not in [x.split()[0] for x in idx_cols]:
                            idx_cols.append(sc)
                    for rc in finfo["range_cols"]:
                        if rc not in [x.split()[0] for x in idx_cols]:
                            idx_cols.append(rc)

                    if idx_cols:
                        safe_col_slug = "_".join(re.sub(r"[^\w]", "_", c.split()[0]).strip("_") for c in idx_cols[:3])
                        include_cols: list[str] = []
                        for key_cand in (node.alias, rel):
                            if key_cand and key_cand in sql_ctx["select_cols_by_alias"]:
                                for scol in sql_ctx["select_cols_by_alias"][key_cand]:
                                    if scol not in [x.split()[0] for x in idx_cols] and scol not in include_cols:
                                        include_cols.append(scol)
                        include_clause = f"\n    INCLUDE ({', '.join(include_cols[:4])})" if include_cols else ""
                        ddl = (
                            f"CREATE INDEX CONCURRENTLY idx_{rel}_{safe_col_slug}\n"
                            f"    ON {rel} ({', '.join(idx_cols)}){include_clause};"
                        )
                        if ddl not in seen_index_ddl:
                            seen_index_ddl.add(ddl)
                            why_idx = (
                                f"Follows the B-Tree Equality -> Sort/Range rule on `{rel}`: filters on "
                                f"`{', '.join(idx_cols)}`"
                            )
                            if sort_cols:
                                why_idx += f" and provides pre-sorted order for `{', '.join(sort_cols)}` to eliminate the parent Sort step"
                            if include_cols:
                                why_idx += f", while `INCLUDE ({', '.join(include_cols[:4])})` enables an Index Only Scan without heap fetches"
                            why_idx += "."
                            index_changes.append({
                                "table": rel,
                                "type": "Composite / Covering B-Tree Index",
                                "ddl": ddl,
                                "why": why_idx,
                                "verify_sql": f"ANALYZE {rel};",
                            })

                # Check if filter uses non-sargable function wrapper on column
                if finfo["func_exprs"]:
                    fe = finfo["func_exprs"][0]
                    if fe.startswith(("date(", "date_trunc(")):
                        col_inside = re.sub(r"^.*?\(|\).*$", "", fe)
                        rw_key = f"sargable_date_{rel}_{col_inside}"
                        if rw_key not in seen_rewrites:
                            seen_rewrites.add(rw_key)
                            query_rewrites.append({
                                "title": f"Make `{fe}` sargable with a direct timestamp range predicate",
                                "why": f"Wrapping `{col_inside}` in `{fe}` forces PostgreSQL to evaluate the function on every row before filtering, preventing standard B-Tree index seeks on `{col_inside}`.",
                                "before_sql": f"WHERE {filter_expr.strip('()')}",
                                "after_sql": f"WHERE {col_inside} >= '2026-01-01 00:00:00'\n  AND {col_inside} <  '2026-02-01 00:00:00'",
                            })

        # 2. Index Scan / Index Only Scan with high Filter discard or high Heap Fetches
        if "index scan" in ntype_l or "index only scan" in ntype_l:
            filter_expr = props.get("Filter", "")
            idx_cond = props.get("Index Cond", "")
            if rows_removed_filter >= 500 or (rows_removed_filter > 0 and node.exclusive_ms >= 10.0):
                finfo = _extract_filter_columns(filter_expr, node.relation, node.alias)
                icinfo = _extract_filter_columns(idx_cond, node.relation, node.alias)
                warn_msg = (
                    f"Index `{node.index_name}` matched via `{idx_cond}`, but PostgreSQL still had to fetch heap tuples and discard "
                    f"{rows_removed_filter:,} rows in memory using `Filter: {filter_expr}`."
                )
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "warning" if node.pct_of_total < 40 else "critical",
                    "node_id": node.node_id,
                    "title": f"Under-selective Index Scan on `{rel}` (`{node.index_name}`)",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.raw_header}` spent {node.exclusive_ms:.2f} ms ({node.pct_of_total}%) fetching and filtering heap rows.",
                    "why": warn_msg,
                })
                combined_cols: list[str] = []
                for c in icinfo["eq_cols"] + finfo["eq_cols"] + icinfo["range_cols"] + finfo["range_cols"]:
                    if c not in combined_cols:
                        combined_cols.append(c)
                if combined_cols:
                    slug = "_".join(combined_cols[:3])
                    ddl = f"CREATE INDEX CONCURRENTLY idx_{rel}_{slug}\n    ON {rel} ({', '.join(combined_cols)});"
                    if ddl not in seen_index_ddl:
                        seen_index_ddl.add(ddl)
                        index_changes.append({
                            "table": rel,
                            "type": "Expanded Composite B-Tree Index (Eliminate Post-Index Heap Filter)",
                            "ddl": ddl,
                            "why": f"Extends `{node.index_name}` to include the filtered column(s) (`{', '.join(finfo['eq_cols'] + finfo['range_cols'])}`) inside the index key so rows are filtered at the index level without random heap page fetches.",
                            "verify_sql": f"ANALYZE {rel};",
                        })

            if "index only scan" in ntype_l and heap_fetches > 1000:
                warn_msg = (
                    f"Index Only Scan on `{node.index_name}` still performed {heap_fetches:,} Heap Fetches because visibility map bits were not set on `{rel}`."
                )
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "warning",
                    "node_id": node.node_id,
                    "title": f"High Heap Fetches ({heap_fetches:,}) during Index Only Scan on `{rel}`",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.raw_header}` required {heap_fetches:,} heap visibility checks ({node.exclusive_ms:.2f} ms).",
                    "why": warn_msg,
                })
                skey = f"vacuum_{rel}"
                if skey not in seen_settings:
                    seen_settings.add(skey)
                    setting_changes.append({
                        "parameter": f"VACUUM (ANALYZE) {rel} + autovacuum_vacuum_scale_factor",
                        "command": (
                            f"VACUUM (ANALYZE) {rel};\n"
                            f"ALTER TABLE {rel} SET (\n"
                            f"    autovacuum_vacuum_scale_factor = 0.02,\n"
                            f"    autovacuum_analyze_scale_factor = 0.01\n"
                            f");"
                        ),
                        "why": f"Index Only Scans must visit the heap for any page whose all-visible bit is unset in the Visibility Map. Running `VACUUM` and lowering `autovacuum_vacuum_scale_factor` on `{rel}` keeps pages marked all-visible.",
                    })

        # 3. Bitmap Heap Scan with lossy pages or high recheck discard
        if "bitmap heap scan" in ntype_l:
            heap_blocks_str = props.get("Heap Blocks", "")
            m_lossy = re.search(r"lossy=(\d+)", heap_blocks_str, flags=re.IGNORECASE)
            lossy_blocks = int(m_lossy.group(1)) if m_lossy else 0
            if lossy_blocks > 0:
                lossy_mb = round((lossy_blocks * BLOCK_SIZE_KB) / 1024.0, 2)
                rec_mb = max(16, int(((lossy_blocks * BLOCK_SIZE_KB) / 1024.0) * 2.5))
                warn_msg = (
                    f"Bitmap overflowed `work_mem` and degraded to {lossy_blocks:,} lossy heap blocks (~{lossy_mb} MiB), "
                    f"forcing PostgreSQL to recheck every tuple in those pages ({rows_removed_recheck:,} rows discarded by recheck)."
                )
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "critical" if node.pct_of_total >= 30 else "warning",
                    "node_id": node.node_id,
                    "title": f"Lossy Bitmap Heap Scan on `{rel}` ({lossy_blocks:,} lossy blocks)",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.raw_header}` degraded to page-level lossy bitmap tracking ({node.exclusive_ms:.2f} ms).",
                    "why": warn_msg,
                })
                skey = "work_mem_bitmap"
                if skey not in seen_settings:
                    seen_settings.add(skey)
                    setting_changes.append({
                        "parameter": "work_mem (Eliminate Lossy Bitmap Degradation)",
                        "command": f"SET LOCAL work_mem = '{rec_mb}MB';",
                        "why": f"A TID bitmap turns lossy when its size exceeds `work_mem`. Raising `work_mem` to `{rec_mb}MB` for this session/role keeps exact tuple pointers in memory and eliminates the {rows_removed_recheck:,} recheck discards.",
                    })

            b_filter = props.get("Filter", "")
            if rows_removed_filter >= 1000 and b_filter:
                bf_info = _extract_filter_columns(b_filter, node.relation, node.alias)
                if bf_info["has_leading_wildcard"]:
                    col_m = re.search(
                        r"([a-zA-Z_]\w*)\s*(?:~~\*?|I?LIKE)\s*'%([^']+)'",
                        bf_info.get("cleaned_expr", b_filter),
                        re.IGNORECASE,
                    )
                    tcol = col_m.group(1) if col_m else "email"
                    ddl = (
                        f"CREATE EXTENSION IF NOT EXISTS pg_trgm;\n"
                        f"CREATE INDEX CONCURRENTLY idx_{rel}_{tcol}_trgm\n"
                        f"    ON {rel} USING gin ({tcol} gin_trgm_ops);"
                    )
                    if ddl not in seen_index_ddl:
                        seen_index_ddl.add(ddl)
                        index_changes.append({
                            "table": rel,
                            "type": "GIN Trigram Index (Accelerate Leading-Wildcard Filter on Bitmap Heap Scan)",
                            "ddl": ddl,
                            "why": f"After the bitmap index scan on `{props.get('Recheck Cond', '')}`, PostgreSQL still discarded {rows_removed_filter:,} heap rows checking `{b_filter}`. A `pg_trgm` GIN index (or storing a reversed domain column `reverse(lower({tcol}))`) lets Postgres intersect both bitmaps before visiting the heap.",
                            "verify_sql": f"ANALYZE {rel};",
                        })
                    rw_key = f"reverse_suffix_{rel}_{tcol}"
                    if rw_key not in seen_rewrites and "%@" in b_filter:
                        seen_rewrites.add(rw_key)
                        query_rewrites.append({
                            "title": f"Replace leading-wildcard `ILIKE '%@...'` with an indexed `reverse(lower({tcol}))` prefix or generated domain column",
                            "why": f"Suffix matching (`%@domain.com`) cannot use a standard B-Tree index. Indexing `lower(split_part({tcol}, '@', 2))` or `reverse(lower({tcol}))` turns a full-heap scan into a direct B-Tree equality lookup.",
                            "before_sql": f"WHERE {tcol} ILIKE '%@enterprise-client.com'",
                            "after_sql": f"-- With expression index: CREATE INDEX CONCURRENTLY ON {rel} ( org_id, lower(split_part({tcol}, '@', 2)) );\nWHERE org_id = 108\n  AND lower(split_part({tcol}, '@', 2)) = 'enterprise-client.com'",
                        })

        # 4. Sort / Incremental Sort spilling to disk or taking high time
        if ntype_l in ("sort", "incremental sort"):
            sort_method = props.get("Sort Method", "")
            sort_key = props.get("Sort Key", "")
            m_disk = re.search(r"external\s+(?:merge|sort)\s+Disk:\s*(\d+)kB", sort_method, flags=re.IGNORECASE)
            if m_disk or node.temp_written > 0:
                disk_kb = int(m_disk.group(1)) if m_disk else (node.temp_written * BLOCK_SIZE_KB)
                disk_mb = round(disk_kb / 1024.0, 2)
                rec_wm_mb = max(32, int((disk_kb / 1024.0) * 2.2))
                warn_msg = (
                    f"Sort on `{sort_key}` spilled {disk_kb:,} KiB ({disk_mb} MiB) to temporary disk files (`{sort_method}`)."
                )
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "critical",
                    "node_id": node.node_id,
                    "title": f"External Disk Sort Spill ({disk_mb} MiB temp I/O)",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.node_type}` took {node.exclusive_ms:.2f} ms self time ({node.pct_of_total}%) sorting {node.total_actual_rows:,} rows on disk.",
                    "why": warn_msg,
                })
                skey = "work_mem_sort"
                if skey not in seen_settings:
                    seen_settings.add(skey)
                    setting_changes.append({
                        "parameter": "work_mem (Prevent External Merge Disk Sort)",
                        "command": (
                            f"-- Session / transaction level (safe against OOM across concurrent connections):\n"
                            f"SET LOCAL work_mem = '{rec_wm_mb}MB';"
                        ),
                        "why": f"The sort required {disk_mb} MiB on disk (`{sort_method}`). In-memory quicksort needs ~1.5x-2x the external merge disk footprint, so `{rec_wm_mb}MB` allows the sort to complete entirely in RAM.",
                    })
            elif node.exclusive_ms >= 15.0 and node.pct_of_total >= 15.0:
                warn_msg = f"In-memory sort on `{sort_key}` across {node.total_actual_rows:,} rows consumed {node.exclusive_ms:.2f} ms."
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "warning",
                    "node_id": node.node_id,
                    "title": f"Heavy In-Memory Sort on `{sort_key}`",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.node_type}` spent {node.exclusive_ms:.2f} ms ({node.pct_of_total}%) sorting {node.total_actual_rows:,} rows.",
                    "why": warn_msg,
                })

        # 5. Hash / HashAggregate multi-batch temp spill
        if "hash" in ntype_l:
            batches_str = props.get("Batches", "1")
            m_batch = re.search(r"(\d+)", batches_str)
            batches = int(m_batch.group(1)) if m_batch else 1
            if batches > 1 or node.temp_written > 0:
                spill_mb = round((max(node.temp_written, node.temp_read) * BLOCK_SIZE_KB) / 1024.0, 2)
                rec_wm = max(64, int(spill_mb * 2.5))
                warn_msg = (
                    f"`{node.node_type}` spilled across {batches} batches to temporary disk files (~{spill_mb} MiB temp I/O)."
                )
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "critical",
                    "node_id": node.node_id,
                    "title": f"Multi-Batch {node.node_type} Temp Disk Spill ({batches} batches)",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`{node.node_type}` took {node.exclusive_ms:.2f} ms ({node.pct_of_total}%) spilling hash partitions to disk.",
                    "why": warn_msg,
                })
                skey = "work_mem_hash"
                if skey not in seen_settings:
                    seen_settings.add(skey)
                    setting_changes.append({
                        "parameter": "work_mem / hash_mem_multiplier",
                        "command": (
                            f"SET LOCAL work_mem = '{rec_wm}MB';\n"
                            f"SET LOCAL hash_mem_multiplier = 2.0;"
                        ),
                        "why": f"When a Hash table exceeds `work_mem * hash_mem_multiplier`, PostgreSQL splits it into {batches} disk batches. Raising `work_mem` to `{rec_wm}MB` keeps the hash table in Batch 1 (pure memory).",
                    })

        # 6. Nested Loop with high outer rows or severe row underestimation
        if "nested loop" in ntype_l and len(node.children) >= 2:
            outer_ch, inner_ch = node.children[0], node.children[1]
            if inner_ch.actual_loops >= 500 and node.inclusive_ms >= 20.0:
                est_note = ""
                if outer_ch.row_est_direction == "underestimated":
                    est_note = (
                        f" The planner estimated only {outer_ch.plan_rows:,} outer rows from `{outer_ch.raw_header}` "
                        f"but actually received {outer_ch.actual_rows:,} rows ({outer_ch.row_est_factor}x underestimate), "
                        f"tricking it into picking a Nested Loop instead of a Hash Join."
                    )
                warn_msg = (
                    f"Nested Loop drove `{inner_ch.raw_header}` {inner_ch.actual_loops:,} times, accounting for {node.inclusive_ms:.2f} ms inclusive time.{est_note}"
                )
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "critical",
                    "node_id": node.node_id,
                    "title": f"High-Iteration Nested Loop ({inner_ch.actual_loops:,} inner probes)",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": round(min(100.0, (node.inclusive_ms / total_time_ms) * 100.0), 1),
                    "what_is_slow": f"`Nested Loop` executed its inner child `{inner_ch.raw_header}` {inner_ch.actual_loops:,} times ({node.inclusive_ms:.2f} ms total).",
                    "why": warn_msg,
                })
                if outer_ch.row_est_direction == "underestimated":
                    t_rel = outer_ch.relation or rel
                    skey = f"analyze_{t_rel}"
                    if skey not in seen_settings:
                        seen_settings.add(skey)
                        fcols = _extract_filter_columns(outer_ch.properties.get("Filter", "") + " " + outer_ch.properties.get("Index Cond", ""))["eq_cols"]
                        ext_stats = ""
                        if len(fcols) >= 2 and t_rel != "target_table":
                            ext_stats = (
                                f"\n-- If columns ({', '.join(fcols[:3])}) are correlated, teach the planner with extended statistics:\n"
                                f"CREATE STATISTICS IF NOT EXISTS st_{t_rel}_{'_'.join(fcols[:2])}\n"
                                f"    (dependencies, ndistinct, mcv) ON {', '.join(fcols[:3])} FROM {t_rel};\n"
                                f"ANALYZE {t_rel};"
                            )
                        setting_changes.append({
                            "parameter": f"ANALYZE {t_rel} & Extended Statistics (Fix {outer_ch.row_est_factor}x Row Underestimate)",
                            "command": f"ANALYZE {t_rel};{ext_stats}",
                            "why": f"The planner chose a Nested Loop because it thought `{t_rel}` would return {outer_ch.plan_rows:,} rows instead of {outer_ch.actual_rows:,}. Updating table statistics (and adding multivariate `CREATE STATISTICS` if filter columns are correlated) allows the optimizer to switch to a Hash Join.",
                        })

            if rows_removed_join >= 1000:
                jfilter = props.get("Join Filter", "")
                warn_msg = f"Cartesian/non-indexed Nested Loop discarded {rows_removed_join:,} row pairs via `Join Filter: {jfilter}`."
                node.warnings.append(warn_msg)
                findings.append({
                    "severity": "critical",
                    "node_id": node.node_id,
                    "title": f"Nested Loop Join Filter Rejected {rows_removed_join:,} Row Combinations",
                    "exclusive_ms": node.exclusive_ms,
                    "inclusive_ms": node.inclusive_ms,
                    "pct_of_total": node.pct_of_total,
                    "what_is_slow": f"`Nested Loop` evaluated `Join Filter: {jfilter}` in CPU and rejected {rows_removed_join:,} rows.",
                    "why": warn_msg,
                })

        # 7. Correlated SubPlan executed in a loop
        if node.subplan_name and "subplan" in node.subplan_name.lower() and node.actual_loops > 1:
            warn_msg = (
                f"Correlated `{node.subplan_name}` executed {node.actual_loops:,} times (once per outer row), "
                f"consuming {node.inclusive_ms:.2f} ms."
            )
            node.warnings.append(warn_msg)
            findings.append({
                "severity": "critical",
                "node_id": node.node_id,
                "title": f"Correlated {node.subplan_name} Executed {node.actual_loops:,} Times",
                "exclusive_ms": node.exclusive_ms,
                "inclusive_ms": node.inclusive_ms,
                "pct_of_total": round(min(100.0, (node.inclusive_ms / total_time_ms) * 100.0), 1),
                "what_is_slow": f"`{node.subplan_name}` (`{node.raw_header}`) ran {node.actual_loops:,} times ({node.inclusive_ms:.2f} ms total).",
                "why": warn_msg,
            })
            rw_key = "correlated_subplan_rewrite"
            if rw_key not in seen_rewrites:
                seen_rewrites.add(rw_key)
                query_rewrites.append({
                    "title": f"Replace correlated `{node.subplan_name}` with a single derived-table JOIN or Window Function",
                    "why": f"A correlated subquery in `SELECT` or `WHERE` forces PostgreSQL to execute `{node.raw_header}` once per outer row ({node.actual_loops:,} loops). Pre-aggregating once in a CTE/derived table or using `EXISTS` turns O(N) probes into a single pass.",
                    "before_sql": sql_text.strip() or f"-- Correlated subquery executing {node.actual_loops:,} times on {rel}",
                    "after_sql": (
                        f"WITH aggregated_{rel} AS (\n"
                        f"    SELECT foreign_key_id, COUNT(*) AS cnt, MAX(created_at) AS latest_at\n"
                        f"    FROM {rel}\n"
                        f"    GROUP BY foreign_key_id\n"
                        f")\n"
                        f"SELECT t.*, a.cnt, a.latest_at\n"
                        f"FROM primary_table t\n"
                        f"LEFT JOIN aggregated_{rel} a ON a.foreign_key_id = t.id;"
                    ),
                })

        # 8. Standalone severe row estimation mismatch not already caught by Nested Loop
        if (
            node.has_actuals
            and not node.never_executed
            and node.row_est_factor >= 15.0
            and abs(node.actual_rows - node.plan_rows) >= 1000
            and node.relation
        ):
            skey = f"analyze_{node.relation}"
            if skey not in seen_settings:
                seen_settings.add(skey)
                setting_changes.append({
                    "parameter": f"ANALYZE {node.relation} (Row Estimate Off by {node.row_est_factor}x)",
                    "command": (
                        f"ANALYZE {node.relation};\n"
                        f"-- If skew persists on filtered columns, increase statistics histogram buckets (default 100):\n"
                        f"-- ALTER TABLE {node.relation} ALTER COLUMN <skewed_col> SET STATISTICS 500;\n"
                        f"-- ANALYZE {node.relation};"
                    ),
                    "why": f"On `{node.raw_header}`, the planner estimated {node.plan_rows:,} rows per loop but got {node.actual_rows:,} rows ({node.row_est_factor}x {node.row_est_direction}). Stale `pg_statistic` histograms or low statistics targets cause poor join/scan choices.",
                })

    # SQL-level rewrites detected from the query text + plan
    if sql_ctx.get("offset_val") and sql_ctx["offset_val"] >= 500:
        off = sql_ctx["offset_val"]
        lim = sql_ctx.get("limit_val") or 50
        ord_col = (sql_ctx["order_by_cols"][0] if sql_ctx["order_by_cols"] else "created_at DESC, id DESC")
        base_col = ord_col.split()[0]
        op = "<" if "DESC" in ord_col.upper() else ">"
        query_rewrites.append({
            "title": f"Replace deep `OFFSET {off:,}` pagination with Keyset (Seek) Pagination",
            "why": f"`OFFSET {off:,} LIMIT {lim}` forces PostgreSQL to fetch, sort, and step over {off + lim:,} rows only to discard the first {off:,}. Keyset pagination seeks directly via a B-Tree index in O(log N) time.",
            "before_sql": f"ORDER BY {ord_col}\nLIMIT {lim} OFFSET {off}",
            "after_sql": f"WHERE {base_col} {op} :last_seen_{base_col.split('.')[-1]}\nORDER BY {ord_col}\nLIMIT {lim}",
        })

    if sql_ctx.get("has_not_in"):
        query_rewrites.append({
            "title": "Rewrite `NOT IN (SELECT ...)` as `NOT EXISTS` (Anti-Join)",
            "why": "In PostgreSQL, `NOT IN (SELECT ...)` uses three-valued NULL logic that often prevents hashed/indexed Anti-Joins (producing a slow SubPlan scan) and returns 0 rows if any NULL exists in the subquery.",
            "before_sql": "WHERE user_id NOT IN (SELECT user_id FROM blocked_users)",
            "after_sql": "WHERE NOT EXISTS (\n    SELECT 1 FROM blocked_users b\n    WHERE b.user_id = t.user_id\n)",
        })

    if sql_ctx.get("select_star") and any("seq scan" in n.node_type.lower() or "sort" in n.node_type.lower() for n in all_nodes):
        query_rewrites.append({
            "title": "Replace `SELECT *` with explicit projection columns",
            "why": "`SELECT *` widens the tuple width (`width=` in EXPLAIN), increasing sort memory footprint in `work_mem`, preventing Index Only Scans, and pulling toasted/wide columns across the wire.",
            "before_sql": "SELECT * FROM ...",
            "after_sql": "SELECT id, status, created_at, total_amount -- only required columns\nFROM ...",
        })

    # High buffer read ratio (cold cache / I/O bound) recommendation
    if total_shared_read >= 2500 and (cache_hit_ratio is not None and cache_hit_ratio < 85.0):
        setting_changes.append({
            "parameter": "shared_buffers / random_page_cost / track_io_timing",
            "command": (
                "-- Check if I/O wait dominates execution:\n"
                "SET LOCAL track_io_timing = on;\n"
                "-- Ensure SSD planner cost modeling matches reality (default is 4.0 for spinning disks):\n"
                "SET random_page_cost = 1.1;\n"
                "SET effective_cache_size = '75% of total RAM';"
            ),
            "why": f"The query read {total_shared_read:,} blocks ({shared_read_mb} MiB) from OS/disk storage with a buffer cache hit ratio of only {cache_hit_ratio}%. Lowering `random_page_cost` to `1.1` on SSD storage and eliminating full scans via the recommended index will drop physical reads.",
        })

    # If cost-only EXPLAIN without ANALYZE was pasted, surface a clear note
    if not has_any_actuals:
        setting_changes.insert(0, {
            "parameter": "Run with EXPLAIN (ANALYZE, BUFFERS) for runtime actuals",
            "command": f"EXPLAIN (ANALYZE, BUFFERS, SETTINGS)\n{sql_text.strip() or 'SELECT ...;'}",
            "why": "The pasted plan contains planner cost estimates (`cost=... rows=...`) without runtime actuals (`actual time=...`). Re-running with `(ANALYZE, BUFFERS)` exposes actual loop counts, row misestimates, and temp/disk block reads.",
        })

    # Sort findings by exclusive_ms descending
    findings.sort(key=lambda f: (0 if f["severity"] == "critical" else 1, -f["exclusive_ms"]))

    # Determine overall health verdict
    is_healthy = (
        has_any_actuals
        and total_time_ms < 15.0
        and total_temp_written == 0
        and not any(f["severity"] == "critical" for f in findings)
    )

    if is_healthy:
        verdict = "Healthy & Well-Indexed Execution Plan"
        headline_summary = (
            f"This query completed in {total_time_ms:.2f} ms with zero disk spills and no bottleneck scans. "
            f"No new indexes or query rewrites are needed — adding extra indexes here would only add write amplification and WAL overhead."
        )
    elif findings:
        top_f = findings[0]
        verdict = "Critical Bottleneck Detected" if top_f["severity"] == "critical" else "Optimization Opportunity Detected"
        headline_summary = (
            f"Primary bottleneck: {top_f['title']} ({top_f['exclusive_ms']:.2f} ms self time, {top_f['pct_of_total']}% of {total_time_ms:.2f} ms total). "
            f"{top_f['why']}"
        )
    else:
        top_node = max(all_nodes, key=lambda x: x.exclusive_ms)
        verdict = "Review Highest-Cost Node"
        headline_summary = (
            f"Highest time consumer is `{top_node.raw_header}` at {top_node.exclusive_ms:.2f} ms ({top_node.pct_of_total}% of total)."
        )

    # Build Lead DBA Interview & Ticket Playbook talking points tailored to this specific plan
    interview_playbook = _build_lead_dba_playbook(
        total_time_ms=total_time_ms,
        planning_time_ms=planning_time_ms,
        is_healthy=is_healthy,
        findings=findings,
        index_changes=index_changes,
        query_rewrites=query_rewrites,
        setting_changes=setting_changes,
        shared_read_mb=shared_read_mb,
        temp_spill_mb=temp_spill_mb,
        cache_hit_ratio=cache_hit_ratio,
    )

    return {
        "verdict": verdict,
        "is_healthy": is_healthy,
        "has_actuals": has_any_actuals,
        "headline_summary": headline_summary,
        "metrics": {
            "execution_time_ms": total_time_ms,
            "planning_time_ms": planning_time_ms,
            "total_nodes": len(all_nodes),
            "shared_hit_blocks": total_shared_hit,
            "shared_read_blocks": total_shared_read,
            "shared_hit_mb": shared_hit_mb,
            "shared_read_mb": shared_read_mb,
            "temp_spill_mb": temp_spill_mb,
            "cache_hit_ratio": cache_hit_ratio,
        },
        "tree": [_serialize_tree(r) for r in roots],
        "findings": findings,
        "recommendations": {
            "indexes": index_changes,
            "rewrites": query_rewrites,
            "settings": setting_changes,
        },
        "interview_playbook": interview_playbook,
    }


def _build_lead_dba_playbook(
    total_time_ms: float,
    planning_time_ms: float,
    is_healthy: bool,
    findings: list[dict[str, Any]],
    index_changes: list[dict[str, Any]],
    query_rewrites: list[dict[str, Any]],
    setting_changes: list[dict[str, Any]],
    shared_read_mb: float,
    temp_spill_mb: float,
    cache_hit_ratio: float | None,
) -> dict[str, Any]:
    if is_healthy:
        return {
            "thirty_second_diagnosis": (
                f"\"This plan executes in {total_time_ms:.2f} ms using selective index access with high shared-buffer locality "
                f"({cache_hit_ratio if cache_hit_ratio is not None else 100}% cache hit) and zero temp file spills. "
                f"As a Lead DBA, my recommendation is to make no schema changes — over-indexing degrades HOT updates and increases WAL and vacuum overhead.\""
            ),
            "production_rollout_checklist": [
                "Verify `calls` and `total_exec_time` in `pg_stat_statements` — if a 0.3 ms query is top of CPU, the problem is N+1 query volume from the application, not single-query plan efficiency.",
                "If `Heap Fetches` grows over time on an Index Only Scan, check `pg_stat_user_tables.n_dead_tup` and tune per-table `autovacuum_vacuum_scale_factor`.",
            ],
            "follow_up_questions": [
                {
                    "q": "When would a sub-millisecond query still cause a P1 database outage?",
                    "a": "When called 50,000+ times/sec from an application N+1 loop without connection pooling (PgBouncer), saturating CPU context switches or lightweight lock (`LWLock:BufferMapping`) contention.",
                }
            ],
        }

    top_finding = findings[0]["title"] if findings else "the highest exclusive-time scan node"
    top_why = findings[0]["why"] if findings else ""
    first_fix = (
        index_changes[0]["ddl"].splitlines()[0]
        if index_changes
        else (query_rewrites[0]["title"] if query_rewrites else (setting_changes[0]["parameter"] if setting_changes else "targeted indexing"))
    )

    checklist: list[str] = []
    if index_changes:
        checklist.append(
            "Always run `CREATE INDEX CONCURRENTLY` outside a transaction block with `SET lock_timeout = '3s'; SET statement_timeout = '0';` and raise `maintenance_work_mem = '1GB'` in the session to build the index fast without blocking DML."
        )
        checklist.append(
            "Before creating a new index on a write-heavy table, check `pg_stat_user_indexes` for redundant prefix indexes and check `n_tup_upd` / `n_tup_hot_upd` so you don't break Heap-Only Tuple (HOT) updates."
        )
    if setting_changes:
        checklist.append(
            "Scope `work_mem` increases with `SET LOCAL work_mem = ...` or `ALTER ROLE <app_user> SET work_mem = ...` rather than globally in `postgresql.conf`, because every parallel worker and hash/sort node in a query can allocate `work_mem` simultaneously."
        )
    checklist.append(
        "Validate before/after improvement using `EXPLAIN (ANALYZE, BUFFERS)` and track `mean_exec_time` + `shared_blks_read` regression in `pg_stat_statements`."
    )

    follow_ups: list[dict[str, str]] = [
        {
            "q": "What if `CREATE INDEX CONCURRENTLY` fails halfway due to a deadlock or unique violation?",
            "a": "It leaves behind an `INVALID` index that still consumes write overhead on INSERT/UPDATE. Check `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`, drop it with `DROP INDEX CONCURRENTLY`, and rebuild.",
        },
        {
            "q": "Why can't you just set `work_mem = 256MB` globally on a server with 64 GB RAM?",
            "a": "Because `work_mem` is allocated per sort/hash operation per connection. 300 active connections running queries with 3 sort/hash nodes each could allocate `300 * 3 * 256MB = 230 GB`, triggering the Linux OOM killer on the postmaster.",
        },
    ]

    return {
        "thirty_second_diagnosis": (
            f"\"Looking at exclusive node times rather than just total cost, the bottleneck is {top_finding}. "
            f"{top_why} "
            f"{f'It pulled {shared_read_mb} MiB from storage' if shared_read_mb > 0 else ''}"
            f"{f' and spilled {temp_spill_mb} MiB to temp disk files' if temp_spill_mb > 0 else ''}. "
            f"The primary fix is `{first_fix}`, verified via `EXPLAIN (ANALYZE, BUFFERS)`.\""
        ),
        "production_rollout_checklist": checklist,
        "follow_up_questions": follow_ups,
    }
