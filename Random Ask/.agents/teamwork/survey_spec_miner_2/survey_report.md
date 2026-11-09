# Antigravity Skill Specification (SKILL.md) Survey & Mining Report

**Document Status**: Authoritative Specification Report  
**Author**: `survey_spec_miner_2` (Antigravity Spec Miner)  
**Investigation Scope**: Antigravity Customization Architecture, Runtime Binary (`language_server`), Built-in Skills (`builtin/skills/*`), Customization Documentation (`agy-customizations/docs/*`), and Skill Execution Mechanics  
**Date**: November 2026 (Investigation Timestamp: 2026-11-06T21:25:00Z)  
**Artifact Path**: `/Users/devesh/Documents/Antigravity/Random Ask/.agents/teamwork/survey_spec_miner_2/survey_report.md`

---

## 1. Executive Summary

This report establishes the authoritative specification, structural schema, metadata conventions, runtime execution lifecycle, and progressive disclosure architecture for Antigravity Skills (`SKILL.md`).

An **Antigravity Skill** is a modular package of domain instructions, multi-step runbooks, progressive references, and optional helper utilities that extends the agent's problem-solving and cognitive capabilities. Unlike static rules (which are unconditionally or conditionally inlined in every prompt) or subagents (which execute in isolated, parallel conversations), skills are **on-demand, progressively disclosed cognitive extensions** that integrate seamlessly into the main conversation loop.

This specification has been mined and cross-verified through three authoritative sources:
1. **The Native Antigravity Runtime**: Dissected the live `language_server` binary (`/Applications/Antigravity.app/Contents/Resources/bin/language_server`), extracting the exact Go runtime parser (`customizations/skills.go`), protobuf definitions (`cortex_pb.WorkflowSpec`), and prompt injection Go templates.
2. **Built-in System Documentation**: Verified official customization specifications in `/Users/devesh/.gemini/antigravity/builtin/skills/agy-customizations/docs/skills.md`, `json_configs.md`, `plugins.md`, and `rules.md`.
3. **Canonical Reference Implementations**: Analyzed all 9 built-in production skills (`agy-customizations`, `antigravity_guide`, `automation`, `generative_ui`, `migrate-workflows`, `permissioned-github`, `plugin`, `run-workflow`, and `ui-plugin-navigation`).

The findings provide the exact blueprint required to implement the upcoming `claude` skill so that any frontier or open-weights model can faithfully emulate Claude's thinking, reasoning, architecture, and planning habits.

---

## 2. Directory Structure & File Layout Conventions

### 2.1 Standard Skill Package Layout

An Antigravity skill must be contained within a dedicated subdirectory named after the skill identifier under a valid customization root:

```text
skills/<skill_name>/
├── SKILL.md          # REQUIRED: Main instruction file with YAML frontmatter
├── references/       # OPTIONAL: Modular deep-dive documentation (Progressive Disclosure)
├── examples/         # OPTIONAL: Reference implementations, few-shot patterns, blueprints
├── resources/        # OPTIONAL: Templates, schemas, checklists, static data assets
└── scripts/          # OPTIONAL: Helper scripts, utilities, verification tools
```

#### Component Responsibilities:
*   **`SKILL.md` (Mandatory)**: The entry point. Contains YAML frontmatter (with `name` and `description`) and concise, high-level workflow instructions. It must not exceed context limits and should link to files in subdirectories for detailed reference.
*   **`references/` (Recommended for Complex Skills)**: Contains granular markdown sub-documentation (e.g., `references/reasoning_protocol.md`, `references/architecture_design.md`). In accordance with Antigravity's **progressive disclosure** principle, files here are *not* injected into the model's initial prompt; the agent reads them on demand via file inspection tools (`view_file`) only when relevant.
*   **`examples/` (Optional)**: Contains concrete examples demonstrating target input/output behavior, complex multi-step trajectories, or exemplary code architectures.
*   **`resources/` (Optional)**: Houses structured data, JSON schemas, evaluation rubrics, or boilerplate templates used during skill execution.
*   **`scripts/` (Optional)**: Houses executable helper scripts (`.sh`, `.py`, `.js`). The agent can execute these via `run_command` to automate deterministic multi-step operations or perform validation.

---

### 2.2 Customization Discovery Roots

The Antigravity runtime automatically traverses and mounts skills from four hierarchical scopes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Discovery Scope Hierarchy                       │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Workspace Project:                                                  │
│    <workspace_root>/.agents/skills/<skill_name>/SKILL.md               │
│    (Also supports .agent/, _agents/, _agent/)                          │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Declared Configs (Workspace):                                       │
│    <workspace_root>/.agents/skills.json (entries, inherits)            │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Global Discovery (User):                                            │
│    ~/.gemini/config/skills/<skill_name>/SKILL.md                       │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Built-in Customizations (App):                                      │
│    /Users/devesh/.gemini/antigravity/builtin/skills/<skill_name>/     │
├────────────────────────────────────────────────────────────────────────┤
│ 5. Declared Configs (Global):                                          │
│    ~/.gemini/config/skills.json                                        │
└────────────────────────────────────────────────────────────────────────┘
```

1.  **Workspace Scope (`.agents/skills/`)**:
    *   Located at `<workspace_root>/.agents/skills/<skill_name>/SKILL.md`.
    *   Alternative supported dot-directories: `.agent/`, `_agents/`, `_agent/`.
    *   Discovered by walking up from the current working directory (CWD) to the repository root (the directory containing `.git` or the opened project root).
    *   Intended for project-specific skills checked into version control (VCS) to be shared with team members.
2.  **Global Scope (`~/.gemini/config/skills/`)**:
    *   Located at `~/.gemini/config/skills/<skill_name>/SKILL.md`.
    *   Applies across all projects and workspaces opened by the user on the machine.
3.  **Plugin Bundle Scope (`plugins/<plugin_name>/skills/`)**:
    *   Located at `plugins/<plugin_name>/skills/<skill_name>/SKILL.md` (either in workspace `.agents/plugins/` or global `~/.gemini/config/plugins/`).
    *   Active only when the containing plugin is enabled.
4.  **Built-in Scope (`builtin/skills/`)**:
    *   Located in the application data directory: `~/.gemini/antigravity/builtin/skills/<skill_name>/SKILL.md`.
    *   Bundled directly with the Antigravity product and mounted by name.

---

### 2.3 Explicit Registration via `skills.json`

For skills stored outside standard paths (e.g., shared submodules, monorepo tool directories), Antigravity supports explicit manifest declaration via `skills.json` placed in a customization root (`.agents/skills.json` or `~/.gemini/config/skills.json`):

```json
{
  "inherits": [
    {
      "path": "/shared/team/skills.json",
      "include_only": ["security-audit"],
      "exclude": ["deprecated-.*"]
    }
  ],
  "entries": [
    {
      "path": "tools/skills",
      "exclude": ["experimental-.*"]
    },
    {
      "path": "~/custom-skills"
    }
  ]
}
```

*   **`entries`** (array): Directories to scan **one level deep** for skill folders containing `SKILL.md`.
*   **`inherits`** (array): Inherits definitions from other shared `skills.json` files.
*   **Path resolution**:
    *   Absolute paths (`/path/...`): Resolved directly against the filesystem.
    *   Home-relative paths (`~/...`): Resolved against the user's home directory.
    *   Relative paths (`path/...`): Resolved relative to the directory containing the dot-directory that declares them, falling back to the workspace root.

---

### 2.4 Loading Priority and Conflict Resolution

When multiple skills share the same `name`, Antigravity resolves collisions strictly by loading priority:

$$\text{Workspace Project} > \text{Declared Workspace Manifest} > \text{Global Discovery} > \text{Built-in Skills} > \text{Global Declared Manifest}$$

*   **Override Behavior**: A skill in `.agents/skills/claude/SKILL.md` completely shadows a global or built-in skill of the same name.
*   **Deduplication**: Customizations are deduplicated by resolved canonical file path. A skill file will never be loaded twice in a single conversation.

---

## 3. Metadata Schema & Frontmatter Specification

### 3.1 YAML Frontmatter Format

Every `SKILL.md` **must** begin with a YAML frontmatter block enclosed between triple-hyphen delimiters (`---`).

```markdown
---
name: claude
description: >-
  Activates Claude's cognitive architecture, metacognitive extended thinking,
  epistemic humility, upfront problem formulation, and robust software engineering
  principles. Use this skill whenever the user requests complex multi-step reasoning,
  system architecture design, rigorous coding, debugging, or execution planning.
disable-slash-command: false
disable-model-invocation: false
metadata:
  icon: psychology
---

# Claude Cognitive & Architectural Framework
...
```

---

### 3.2 Exhaustive Field-by-Field Reference

Based on direct inspection of `language_server`'s `WorkflowSpec` protobuf, `customizations/skills.go`, and production skills, the schema supports the following fields:

| Field Name | Type | Required? | Default | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **`name`** | string | **REQUIRED** | — | Unique identifier for the skill. Must match regex `^[A-Za-z0-9._-]{1,64}$`. Strictly lowercase kebab-case recommended (`claude`, `run-workflow`). Controls the slash command name (`/<name>`). |
| **`description`** | string | **REQUIRED** | — | Concise, highly informative description of what the skill does and **when** the agent should activate it. Primary trigger for autonomous semantic activation. Must use third-person phrasing. |
| **`disable-slash-command`** | boolean | Optional | `false` | When `true`, suppresses creation of the slash command (`/<name>`) in the chat autocomplete menu. Used for skills intended solely for autonomous model invocation (e.g., `ui-plugin-navigation`). |
| **`disable-model-invocation`** | boolean | Optional | `false` | When `true`, prevents the model from automatically activating the skill via semantic matching. The skill can then *only* be invoked manually by the user typing `/<name>`. |
| **`metadata`** | map[string]string | Optional | `{}` | Arbitrary key-value metadata for IDE and UI presentation. Supports `icon` (e.g. `icon: schedule`, `icon: psychology`). |
| **`logo`** | string | Optional | `""` | Path to an icon/logo file (SVG, PNG, JPG, WEBP) relative to the skill folder (e.g., `assets/logo.svg`). Center-cropped, transparent background recommended. |

---

### 3.3 Semantic Activation & The `description` Contract

The `description` field is the single most critical field in `SKILL.md`:
1.  **How the Agent "Sees" Inactive Skills**: Inactive skills are *not* loaded into context. The agent's system prompt receives only a compact catalog entry:
    ```
    - claude (/path/to/skills/claude/SKILL.md): Activates Claude's cognitive architecture... Use this skill whenever...
    ```
2.  **Third-Person "When to Use" Mandate**: The description must explicitly instruct the primary agent on when to trigger the skill.
    *   *Bad*: `"A skill that acts like Claude."` (Model cannot determine trigger conditions).
    *   *Good*: `"Activates Claude's cognitive architecture, metacognitive extended thinking, epistemic humility, and rigorous solution architecture. Use this skill whenever the user asks to plan complex systems, write modular typed code, solve logic puzzles, or perform deep step-by-step reasoning."`
3.  **Slash Command Auto-Generation**: By default (`disable-slash-command: false`), the `name` automatically registers a slash command `/<name>` in the chat interface. Typing `/claude` activates the skill immediately.

---

### 3.4 Runtime Protobuf & Go Model Mapping

Inside Antigravity's `language_server`, a parsed skill is modeled as an `exa.cortex_pb.WorkflowSpec` instance:

```protobuf
message WorkflowSpec {
  string path = 1;                        // Resolved file path to SKILL.md
  string name = 2;                        // Frontmatter name
  string description = 3;                 // Frontmatter description (normalized)
  string content = 4;                     // Markdown body (excluding frontmatter)
  bool is_builtin = 5;                    // True if shipped in builtin/skills
  string scope = 6;                       // "workspace", "global", "plugin"
  string base_dir = 7;                    // Directory containing SKILL.md
  bool disable_model_invocation = 9;      // Frontmatter disable-model-invocation
  bool disable_slash_command = 11;        // Frontmatter disable-slash-command
  string icon = 14;                       // From metadata.icon
  string logo = 15;                       // Resolved relative path or data URI
  string display_name = 18;               // Formatted presentation name
  map<string, string> metadata = 19;      // Additional metadata map
}
```

The Go parser (`customizations.ParseSkillMetadata`) reads the YAML frontmatter, extracts `name` and `description`, executes `workflowparse.NormalizeFrontmatterDescription` to strip trailing whitespaces, validates the `^[A-Za-z0-9._-]{1,64}$` name constraint, and computes a SHA-256 digest (`skillContentDigest`) of the skill directory contents for caching.

---

## 4. Runtime Execution Lifecycle & Progressive Disclosure Mechanics

### 4.1 The Progressive Disclosure Architecture

Large Language Models face context window limits and "attention dilution" when flooded with irrelevant instructions. Antigravity solves this with a **three-tier progressive disclosure model**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Tier 1: Skill Catalog                           │
│  Injected in system prompt: Name + Path + Description (~50 tokens)     │
│  Model evaluates user query against descriptions                       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Model detects relevance OR user types /<name>)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Tier 2: SKILL.md Body                           │
│  Agent executes `view_file` on SKILL.md (~1,500 - 3,000 tokens)        │
│  High-level workflow, cognitive loop, decision trees, relative links   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (Specific complex sub-problem encountered)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     Tier 3: Modular References                         │
│  Agent inspects `references/<doc>.md` only when needed                 │
│  Deep manuals: architecture patterns, formal math, test protocols      │
└────────────────────────────────────────────────────────────────────────┘
```

1.  **Tier 1 (Catalog Registration)**: In the idle/dormant state, the model only sees the skill name, path, and description. This consumes virtually no context budget (~50 tokens per skill).
2.  **Tier 2 (Activation / Ingestion)**: When a user query matches the `description` (or the user issues `/claude`), the model reads the main `SKILL.md` using `view_file`. `SKILL.md` provides the immediate executive workflow, decision matrices, and behavioral rules.
3.  **Tier 3 (Granular On-Demand Fetching)**: `SKILL.md` links to deeper documentation in `references/` via standard Markdown relative links (e.g., `[Cognitive Scratchpad Protocol](./references/extended_thinking.md)`). The agent reads these sub-documents *only* if the current task touches that specific domain.

---

### 4.2 Prompt Injection Templates (Language Server)

Directly reverse-engineered from the `language_server` binary, here is the exact Go template that Antigravity uses to instruct the agent regarding skills:

```gotemplate
You can use specialized 'skills' to help you with complex tasks. Each skill has a name and a description listed below.

Skills are folders of instructions, scripts, and resources that extend your capabilities for specialized tasks. Each skill folder contains:
- **SKILL.md** (required): The main instruction file with YAML frontmatter (name, description) and detailed markdown instructions

More complex skills may include additional directories and files as needed, for example:
- **scripts/** - Helper scripts and utilities that extend your capabilities
- **examples/** - Reference implementations and usage patterns
- **resources/** - Additional files, templates, or assets the skill may reference
- **references/** - Contains additional documentation that agents can read when needed

{{if .Data}}
{{- if .Data.PreloadedSkills}}
Certain skills have been preloaded due to their importance to the current task. The content of their SKILL.md has been injected verbatim below, so you DO NOT need to view them:
{{range .Data.PreloadedSkills -}}
<preloaded_skill name="{{.GetName}}" path="{{.GetPath}}" description="{{.GetDescription}}">
{{.GetContent}}
</preloaded_skill>
{{end -}}
{{end}}
{{- if .Data.Skills}}
If a skill seems relevant to your current task, you MUST read its `SKILL.md` instructions before proceeding. You may skip this step only if you are delegating the skill-related task to a subagent that will read and follow the instructions itself.
When viewing these skill files, always use the exact path provided in the "Available skills" list below.
Available skills:
{{range .Data.Skills -}}
- {{.GetName}} ({{.GetPath}}): {{.GetDescription}}
{{end -}}
{{- end}}
{{- end}}
```

**Key Implications for the `claude` Skill**:
1. When not preloaded, the agent **MUST** call `view_file` on `SKILL.md` as its very first step before generating code or plans.
2. The skill must be written as clear instructions directed at the agent (`"You MUST..."`, `"Follow these steps..."`).
3. Markdown links to `references/` must be formatted cleanly as relative links so `view_file` can resolve them immediately against the skill's base directory.

---

## 5. Specification Miner Findings

### 5.1 Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | File Structure | `SKILL.md` Root File | Main instruction file required in every skill folder. Contains YAML frontmatter and Markdown body. | Markdown text with frontmatter | Parsed `WorkflowSpec` | Missing file causes folder to be ignored as a skill. | `agy-customizations/docs/skills.md` & binary |
| 2 | Frontmatter | `name` field | Unique skill identifier, matching `^[A-Za-z0-9._-]{1,64}$`. | String | Skill ID and slash command name | Parse error if missing or if containing invalid characters/spaces. | Binary Go struct tags & `skills.md` |
| 3 | Frontmatter | `description` field | Natural language trigger describing what skill does and when to use it in 3rd person. | String | System prompt catalog entry | Parse error if missing; without clear "when to use", model fails to activate. | `skills.md` & prompt template |
| 4 | Frontmatter | `disable-slash-command` | Suppresses slash command registration (`/<name>`) in chat autocomplete menu. | Boolean (`true`/`false`) | Flag in `WorkflowSpec` | Defaults to `false`. If invalid type, YAML unmarshal error. | `ui-plugin-navigation/SKILL.md` & binary |
| 5 | Frontmatter | `disable-model-invocation`| Prevents model from autonomously activating skill via semantic prompt matching. | Boolean (`true`/`false`) | Flag in `WorkflowSpec` | Defaults to `false`. Restricts invocation to manual slash command. | Binary strings & protobuf field 9 |
| 6 | Frontmatter | `metadata` map | Key-value store for IDE metadata (e.g., `icon: schedule`). | Map of string:string | UI icon / presentation metadata | Unknown keys ignored silently. | `automation/SKILL.md` & binary struct |
| 7 | Frontmatter | `logo` field | Relative path to skill logo (SVG, PNG, JPG, WEBP). | Relative file path | UI badge rendering | Bad path or URL silently renders no logo. | `plugin.json` / binary `ResolveSkillLogo` |
| 8 | Layout | `references/` Subdir | Subdirectory for bulky, deep documentation split into modular files. | Markdown files | On-demand context | Inactive files never consume tokens until explicitly read. | Canonical skills (`antigravity_guide`) |
| 9 | Layout | `scripts/` Subdir | Subdirectory for executable helper tools and command sequences. | Scripts (`.sh`, `.py`) | Executed via `run_command` | Script errors returned in tool output. | `agy-customizations/docs/skills.md` |
| 10 | Layout | `examples/` Subdir | Subdirectory for reference implementations and few-shot pairs. | Code/Text files | Read by agent on demand | None; static files. | Binary prompt template & `skills.md` |
| 11 | Layout | `resources/` Subdir | Subdirectory for templates, schemas, and static assets. | JSON/YAML/TXT | Read by agent on demand | None; static files. | Binary prompt template & `skills.md` |
| 12 | Discovery | Workspace Discovery | Walks up CWD to git root checking `.agents/skills/`, `.agent/`, `_agents/`, `_agent/`. | Directory tree | Discovered skill specs | Silently ignores non-existent dirs. | `agy-customizations/docs/skills.md` |
| 13 | Discovery | Global Discovery | Scans `~/.gemini/config/skills/` for user-wide skills. | Directory tree | Global skill specs | Silently ignores non-existent dirs. | `agy-customizations/SKILL.md` |
| 14 | Discovery | Plugin Bundle Scoping | Skills packaged inside `plugins/<name>/skills/<skill>/SKILL.md`. | Directory tree | Plugin-scoped skills | Inactive when parent plugin is disabled. | `agy-customizations/docs/plugins.md` |
| 15 | Discovery | `skills.json` Manifest | Explicit registration and path inheritance config file. | JSON file with `entries`, `inherits` | Explicitly mounted skills | Parse error on invalid JSON. Scans 1 level deep. | `agy-customizations/docs/json_configs.md` |
| 16 | Discovery | Built-in Customizations | System-provided skills in `~/.gemini/antigravity/builtin/skills/`. | App bundle files | Built-in skill specs | Read-only; cannot be deleted via API. | Binary `builtin.PopulateBuiltins` |
| 17 | Precedence | Loading Priority | Priority: Workspace > Declared Workspace > Global > Built-in > Declared Global. | Skill lists | Deduplicated skill map | Identically named skills in higher layers shadow lower layers. | `agy-customizations/SKILL.md` |
| 18 | Runtime | Preloaded Skills Block | Runtime injection of critical skills directly into system prompt inside `<preloaded_skill>`. | Preloaded skill list | Verbatim SKILL.md in prompt | Agent does NOT need to call `view_file` for preloaded skills. | Binary Go template in `language_server` |
| 19 | Runtime | Available Skills Catalog| Injects inactive skill names, file paths, and descriptions into prompt. | Discovered skills | Markdown list in prompt | Injects exact absolute path for `view_file`. | Binary Go template in `language_server` |
| 20 | Migration | Workflow to Skill | Automatic conversion of legacy `.agents/workflows/*.md` to `.agents/skills/<name>/SKILL.md`. | Legacy workflow file | Modern skill folder | Overwrite protection: skips if target `SKILL.md` exists. | `migrate-workflows/SKILL.md` |

---

### 5.2 Edge Cases & Observed Behavior

| # | Feature / Area | Input / Edge Case | Observed / Verified Behavior |
|---|----------------|-------------------|------------------------------|
| 1 | Frontmatter Parsing | Missing `name` field in YAML frontmatter | Parse error logged (`"missing name or description in frontmatter"`). Skill is discarded and not registered in Available Skills. |
| 2 | Frontmatter Parsing | Missing `description` field in YAML | Parse error logged. Skill discarded. Model cannot perform semantic routing without description. |
| 3 | Skill Naming | Name containing uppercase letters (e.g. `Claude`) | Allowed by regex `^[A-Za-z0-9._-]{1,64}$`, but canonical conventions dictate lowercase kebab-case (`claude`) for slash command consistency. |
| 4 | Skill Naming | Name with spaces or special symbols (e.g. `claude skill!`) | Fails regex `^[A-Za-z0-9._-]{1,64}$`. Language server rejects the skill definition. |
| 5 | Skill Naming | Name exceeding 64 characters | Fails regex length constraint `{1,64}`. Skill rejected. |
| 6 | Slash Command | Typing `/<name>` when `disable-slash-command: true` | Slash command is not recognized or autocompleted in the chat box. Skill remains discoverable by the model semantically. |
| 7 | Model Invocation | Prompts matching description when `disable-model-invocation: true` | Model will NOT autonomously load the skill. Skill only runs when user explicitly types `/<name>`. |
| 8 | Name Collisions | Workspace skill has same name as Builtin skill (e.g. `automation`) | Workspace skill completely shadows/overrides the Builtin skill (Workspace priority 1 > Builtin priority 4). |
| 9 | Duplicate Discovery | Same skill directory discovered via symlink or parent traversal | Deduplicated by resolved canonical file path (`canonicalizePath`). Loaded exactly once per turn. |
| 10 | File Size / Budget | Bulky `SKILL.md` exceeding context guidelines | Inlines full markdown upon activation; can crowd out conversational context. *Best Practice*: Keep `SKILL.md` under 200 lines and offload specifics to `references/`. |
| 11 | Reference Paths | Markdown relative links (e.g. `[protocol](./references/subdoc.md)`) | Model resolves relative link against the `SKILL.md` parent directory and views subdoc using `view_file`. |
| 12 | Windows Path Delimiters | Skill paths inspected on Windows host | Runtime handles both `/` and `\`; documentation recommends POSIX `/` inside markdown links and host separators in UI displays. |
| 13 | Preloaded Skill Handling | Model instructed to read a preloaded skill | Template explicitly instructs: *"Certain skills have been preloaded... The content of their SKILL.md has been injected verbatim below, so you DO NOT need to view them."* Model uses injected text directly. |
| 14 | Unknown Frontmatter | Extra top-level fields (e.g. `version: 1.0`, `author: team`) | Silently ignored by YAML parser if unmapped; does not crash the loader. |
| 15 | `skills.json` Scan Depth| Subdirectories placed two levels deep in an entry directory | `entries` directories are scanned **one level deep only**. Deeper nested folders are not discovered unless explicitly registered. |

---

## 6. Authoritative Production-Ready `SKILL.md` Blueprint

To ensure full compliance with the Antigravity skill architecture, any production-ready skill (and specifically the upcoming `claude` skill) must conform to this exact structural template:

```markdown
---
name: <skill-name>
description: >-
  <What the skill does in third-person>. Use this skill when <specific trigger conditions,
  user tasks, keywords, or domain activities>.
disable-slash-command: false
disable-model-invocation: false
metadata:
  icon: <material_icon_name>
---

# <Skill Title>

<Executive statement defining the role, primary mindset, and core objective of this skill.>

## 1. Operating Principles & Core Protocols
- **Principle 1**: Concise imperative rule.
- **Principle 2**: Concise imperative rule.

## 2. Multi-Step Execution Workflow
1.  **Phase 1: <Phase Name>**:
    - Specific agent action.
    - Reference link: [Detailed Phase Guidelines](./references/<guide>.md)
2.  **Phase 2: <Phase Name>**:
    - Specific agent action.
3.  **Phase 3: <Phase Name>**:
    - Validation and self-correction steps.

## 3. Domain Sub-Modules (Progressive Disclosure)
Depending on the specific sub-task required by the user, read the corresponding reference guide:
- **<Domain 1>**: [references/<guide1>.md](./references/<guide1>.md) — Description of when to read.
- **<Domain 2>**: [references/<guide2>.md](./references/<guide2>.md) — Description of when to read.

## 4. Verification & Output Standards
- Exact criteria for verifying completion.
- Concrete output formatting rules (e.g. zero conversational filler, exact code presentation).
```

---

## 7. Strategic Recommendations for the "Claude" Skill

Synthesizing our specification mining with the cognitive modeling findings from `survey_explorer_1` and the benchmark evaluation taxonomy from `survey_explorer_3`, here are the architectural directives for the builder:

### 7.1 Skill Name and Frontmatter
*   **Name**: `claude`
*   **Slash Command**: `/claude`
*   **Description**:
    ```yaml
    name: claude
    description: >-
      Enables any model to emulate Claude's signature cognitive architecture:
      conversational extended thinking (scratchpad), epistemic humility, non-sycophantic
      calibration, upfront constraint anchoring, and clean, modular software engineering.
      Use this skill whenever the user asks for deep reasoning, complex system architecture,
      defensive coding, rigorous debugging, execution planning, or logic problem solving.
    disable-slash-command: false
    disable-model-invocation: false
    metadata:
      icon: psychology
    ```

### 7.2 Directory Organization & Progressive Disclosure
The `claude` skill must be implemented as a complete multi-file package under `skills/claude/`:

```text
skills/claude/
├── SKILL.md                          # Core cognitive loop & executive rules (~150-200 lines)
├── references/
│   ├── extended_thinking.md          # Conversational scratchpad, pacing, skepticism & pre-computation
│   ├── epistemic_humility.md         # Truth calibration, non-sycophancy, false-premise handling
│   ├── constraint_anchoring.md       # Upfront requirements extraction, quote-anchoring, number tagging
│   ├── architecture_standards.md     # Production engineering, defensive coding, typing, no-fluff delivery
│   └── agentic_discipline.md         # Read-only exploration before mutation, state verification, CLAUDE.md
├── examples/
│   ├── reasoning_trace.md            # Exemplary extended thinking scratchpad trace
│   ├── code_implementation.md        # Exemplary typed, modular, preamble-free code delivery
│   └── pushback_calibration.md       # Exemplary polite but firm correction of erroneous user premise
└── resources/
    ├── execution_checklist.md        # Pre-flight and post-execution verification checklist
    └── error_recovery_matrix.md      # Heuristic fallback rules when tests or assumptions fail
```

### 7.3 Model-Agnostic Dynamic Adaptation
To ensure the skill functions effectively on different underlying models (e.g., Gemini 2.0 Flash, GPT-4o, open-weights models):
1.  **Explicit XML Scratchpad Tagging**: The skill must enforce a `<thinking>` or `<cognitive_scratchpad>` block. On models that do not possess native reasoning traces, this forces the model to deliberate, test edge cases, and self-correct *before* producing user-visible tokens.
2.  **No Host-Colliding Directives**: The skill must instruct the model on *how to think and format solutions*, without attempting to override host environment tools (like replacing `run_command` or `view_file`).
3.  **Zero Conversational Preamble Rule**: The skill must strictly instruct the model to omit conversational pleasantries (*"Certainly! I'd be happy to help..."*), diving straight into the architectural solution or code.

---

## 8. Conclusion

Antigravity provides a robust, native, multi-tiered customizations platform centered on `SKILL.md`. By leveraging YAML frontmatter, progressive disclosure via `references/`, and explicit runtime hooks, a `claude` skill package can be deployed cleanly to elevate any model's cognitive, reasoning, and architectural output.
