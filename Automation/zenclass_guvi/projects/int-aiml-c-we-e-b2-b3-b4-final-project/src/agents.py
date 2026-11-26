"""LangGraph-Style Multi-Agent System: Supervisor, Play-by-Play (Aarav), Analyst (Meera) & Q&A Agent."""

from __future__ import annotations

import time
from typing import Any, Dict

from src.replay_engine import MatchReplayEngine


class CommentaryMultiAgentSystem:
    """
    Coordinates Supervisor routing across two original AI commentator personas
    (Aarav Menon: Play-by-Play; Meera Krishnan: Tactical Stats Analyst) and a Match Q&A Agent.
    100% grounded in Cricsheet ball-by-ball event data & SQL tools to eliminate stat hallucinations.
    """

    PERSONAS = {
        "play_by_play": "Aarav Menon (Play-by-Play)",
        "analyst": "Meera Krishnan (Tactical Analyst)",
        "qa": "Match Stats Copilot",
    }

    def __init__(self, replay_engine: MatchReplayEngine, prompt_version: str = "v2_broadcast_grounded") -> None:
        self.engine = replay_engine
        self.prompt_version = prompt_version

    def generate_ball_commentary(self, match_id: str, seq_index: int, language: str = "English") -> Dict[str, Any]:
        """Supervisor routes live delivery event -> Play-by-Play Agent -> SQL Analyst Agent."""
        t0 = time.perf_counter()
        state = self.engine.get_live_state(match_id, seq_index)
        d = state["latest_delivery"]
        striker = state["striker"]
        bowler = state["bowler"]
        part = state["current_partnership"]

        pbp_line = self._play_by_play_agent(d, state, language)
        analyst_line = self._analyst_agent(d, state, striker, bowler, part, language)
        combined_audio_script = f"{pbp_line} {analyst_line}"
        latency_s = round(time.perf_counter() - t0, 4)

        return {
            "match_id": match_id,
            "seq_index": seq_index,
            "over_ball": f"{d['over_num']}.{d['ball_num']}",
            "language": language,
            "prompt_version": self.prompt_version,
            "play_by_play": {"speaker": self.PERSONAS["play_by_play"], "text": pbp_line},
            "analyst": {"speaker": self.PERSONAS["analyst"], "text": analyst_line},
            "combined_script": combined_audio_script,
            "agent_latency_seconds": latency_s,
            "estimated_tokens": len(combined_audio_script.split()) * 2,
            "state_snapshot": state,
        }

    def _play_by_play_agent(self, d: Dict[str, Any], state: Dict[str, Any], language: str) -> str:
        batter = d["batter"]
        bowler = d["bowler"]
        over_lbl = f"{d['over_num']}.{d['ball_num']}"
        r_bat = int(d["runs_batter"])
        r_ext = int(d["runs_extras"])
        r_tot = int(d["runs_total"])
        is_wkt = bool(d["is_wicket"])
        ext_type = d.get("extras_type") or ""

        if language == "Hindi":
            if is_wkt:
                return f"ओवर {over_lbl}: {bowler} की शानदार गेंद और विकेट! {d['player_out']} ({d['wicket_kind']}) आउट हुए! स्कोर {state['score']}।"
            if r_bat == 6:
                return f"ओवर {over_lbl}: हवा में ऊंचा प्रहार! {batter} ने {bowler} की गेंद पर शानदार छक्का जड़ा! 6 रन, स्कोर {state['score']}।"
            if r_bat == 4:
                return f"ओवर {over_lbl}: बेहतरीन टाइमिंग! {batter} ने गैप में चौका लगाया! 4 रन, स्कोर {state['score']}।"
            if r_ext > 0:
                return f"ओवर {over_lbl}: {bowler} से अतिरिक्त रन ({ext_type}), कुल {r_tot} रन जुड़े। स्कोर {state['score']}।"
            if r_tot == 0:
                return f"ओवर {over_lbl}: {bowler} की सटीक डॉट गेंद, {batter} को कोई रन नहीं मिला। स्कोर {state['score']}।"
            return f"ओवर {over_lbl}: {batter} ने हल्के हाथों से खेलकर {r_tot} रन पूरे किए। स्कोर {state['score']}।"

        if language == "Tamil":
            if is_wkt:
                return f"ஓவர் {over_lbl}: {bowler} அபார பந்துவீச்சு — விக்கெட்! {d['player_out']} ({d['wicket_kind']}) ஆட்டமிழந்தார்! ஸ்கோர் {state['score']}."
            if r_bat == 6:
                return f"ஓவர் {over_lbl}: இமாலய சிக்ஸர்! {bowler} பந்தை {batter} மைதானத்திற்கு வெளியே பறக்கவிட்டார்! 6 ரன்கள், ஸ்கோர் {state['score']}."
            if r_bat == 4:
                return f"ஓவர் {over_lbl}: அற்புதமான பவுண்டரி! {batter} நேர்த்தியாக 4 ரன்கள் அடித்தார்! ஸ்கோர் {state['score']}."
            if r_ext > 0:
                return f"ஓवर {over_lbl}: உதிரி ரன்கள் ({ext_type}) மூலம் {r_tot} ரன் சேர்க்கப்பட்டது. ஸ்கோர் {state['score']}."
            if r_tot == 0:
                return f"ஓவர் {over_lbl}: {bowler} துல்லியமான டாட் பால், {batter} ரன் எடுக்கவில்லை. ஸ்கோர் {state['score']}."
            return f"ஓவர் {over_lbl}: {batter} தட்டிவிட்டு {r_tot} ரன்கள் ஓடி எடுத்தார். ஸ்கோர் {state['score']}."

        # Default English broadcast persona (Aarav Menon)
        if is_wkt:
            fielder_clause = f" — taken by {d['fielders']}" if d.get("fielders") else ""
            return (
                f"{over_lbl} — GONE! Massive breakthrough for {bowler}! "
                f"{d['player_out']} departs ({d['wicket_kind']}{fielder_clause}) and {state['batting_team']} slip to {state['score']}!"
            )
        if r_bat == 6:
            return (
                f"{over_lbl} — SIX! Clean swing of the blade from {batter} off {bowler}, soaring deep into the stands! "
                f"{state['batting_team']} surge to {state['score']}!"
            )
        if r_bat == 4:
            return (
                f"{over_lbl} — FOUR! Crisp placement by {batter}, piercing the infield off {bowler} all along the carpet! "
                f"Score moves to {state['score']}."
            )
        if r_ext > 0:
            return (
                f"{over_lbl} — Extras signaled ({ext_type}) off {bowler}, adding {r_tot} to the total; "
                f"{state['batting_team']} are {state['score']}."
            )
        if r_tot == 0:
            return (
                f"{over_lbl} — Dot ball! {bowler} hits a disciplined length and keeps {batter} watchful on the crease at {state['score']}."
            )
        run_word = "single" if r_tot == 1 else f"{r_tot} runs"
        return (
            f"{over_lbl} — {batter} works {bowler} into the gap for a brisk {run_word}, rotating strike cleanly at {state['score']}."
        )

    def _analyst_agent(
        self,
        d: Dict[str, Any],
        state: Dict[str, Any],
        striker: Dict[str, Any],
        bowler: Dict[str, Any],
        part: Dict[str, Any],
        language: str,
    ) -> str:
        chase_note = ""
        if state["innings_num"] == 2 and state["target"] is not None:
            chase_note = (
                f" Chasing {state['target']}, {state['batting_team']} need {state['runs_needed']} off "
                f"{state['balls_remaining']} balls (RRR {state['required_run_rate']})."
            )

        if language == "Hindi":
            return (
                f"विश्लेषण: {striker['name']} {striker['runs']}({striker['balls']}) पर खेल रहे हैं (स्ट्राइक रेट {striker['strike_rate']}), "
                f"जबकि {bowler['name']} के आंकड़े {bowler['wickets']}/{bowler['runs_conceded']} (इकॉनमी {bowler['economy']}) हैं।"
            )
        if language == "Tamil":
            return (
                f"பகுப்பாய்வு: {striker['name']} {striker['runs']}({striker['balls']}) ரன்களுடன் (SR {striker['strike_rate']}) களத்தில் உள்ளார்; "
                f"{bowler['name']} பந்துவீச்சு {bowler['wickets']}/{bowler['runs_conceded']} (Economy {bowler['economy']})."
            )

        if self.prompt_version == "v1_minimal":
            return f"{striker['name']} has {striker['runs']} off {striker['balls']}. Run rate is {state['current_run_rate']}."

        return (
            f"Tactical lens: {striker['name']} moves to {striker['runs']} off {striker['balls']} balls "
            f"(SR {striker['strike_rate']}, {striker['fours']}x4, {striker['sixes']}x6) in a {part['runs']}-run stand ({part['balls']} balls), "
            f"while {bowler['name']} has figures of {bowler['wickets']}-{bowler['runs_conceded']} ({bowler['overs']} ov, Econ {bowler['economy']}) "
            f"at {state['current_run_rate']} RPO.{chase_note}"
        )

    def answer_viewer_question(self, match_id: str, question: str, seq_index: int | None = None) -> Dict[str, Any]:
        """Natural-language Q&A Agent grounded in live match state & SQL tools."""
        t0 = time.perf_counter()
        q = (question or "").strip()
        if not q:
            raise ValueError("Viewer question cannot be empty.")

        state = self.engine.get_live_state(match_id, seq_index)
        seq = state["seq_index"]
        perf = self.engine.tool_top_performers(match_id, seq)
        meta = state["match_meta"]
        ql = q.lower()

        tools_called = ["get_live_state"]
        if any(k in ql for k in ("top scorer", "highest scorer", "most runs", "leading run", "best batter")):
            tools_called.append("tool_top_performers")
            if perf["top_batters"]:
                tb = perf["top_batters"][0]
                ans = (
                    f"The top run-scorer so far is {tb['batter']} ({tb['batting_team']}) with {tb['runs']} runs "
                    f"off {tb['balls']} balls ({tb['fours']} fours, {tb['sixes']} sixes)."
                )
            else:
                ans = "No runs have been recorded yet."
        elif any(k in ql for k in ("most wickets", "top bowler", "leading wicket", "best bowler", "wickets taken")):
            tools_called.append("tool_top_performers")
            if perf["top_bowlers"]:
                bw = perf["top_bowlers"][0]
                ans = (
                    f"The leading wicket-taker so far is {bw['bowler']} ({bw['bowling_team']}) with "
                    f"{bw['wickets']} wicket(s) for {bw['runs_conceded']} runs."
                )
            else:
                ans = "No wickets have fallen yet."
        elif any(k in ql for k in ("venue", "stadium", "where is", "city")):
            ans = f"This match between {meta['team1']} and {meta['team2']} is being played at {meta['venue']} in {meta['city']}."
        elif "toss" in ql:
            ans = f"{meta['toss_winner']} won the toss and elected to {meta['toss_decision']}."
        elif any(k in ql for k in ("target", "need to win", "runs needed", "chase", "required run rate", "rrr")):
            if state["innings_num"] == 2 and state["target"] is not None:
                ans = (
                    f"Chasing a target of {state['target']}, {state['batting_team']} are {state['score']} ({state['overs']} overs) "
                    f"and need {state['runs_needed']} runs from {state['balls_remaining']} balls at a required run rate of {state['required_run_rate']}."
                )
            else:
                ans = (
                    f"We are still in the first innings: {state['batting_team']} are {state['score']} after {state['overs']} overs "
                    f"(current run rate {state['current_run_rate']})."
                )
        elif any(k in ql for k in ("partnership", "stand")):
            p = state["current_partnership"]
            ans = (
                f"The current unbroken partnership between {state['striker']['name']} and {state['non_striker']['name']} "
                f"is worth {p['runs']} runs off {p['balls']} balls."
            )
        elif any(k in ql for k in ("strike rate", "striker", "batting now", "at the crease")):
            s1, s2 = state["striker"], state["non_striker"]
            ans = (
                f"At the crease are {s1['name']} on {s1['runs']} ({s1['balls']} balls, SR {s1['strike_rate']}) "
                f"and {s2['name']} on {s2['runs']} ({s2['balls']} balls, SR {s2['strike_rate']})."
            )
        elif any(k in ql for k in ("bowler", "bowling", "economy")):
            b = state["bowler"]
            ans = f"{b['name']} is currently bowling with figures of {b['wickets']}-{b['runs_conceded']} in {b['overs']} overs (economy {b['economy']})."
        elif any(k in ql for k in ("winner", "who won", "final result", "player of the match")):
            ans = (
                f"Official Cricsheet match record: {meta['winner']} won ({meta['team1']} vs {meta['team2']} on {meta['match_date']}); "
                f"Player of the Match: {meta['player_of_match'] or 'N/A'}."
            )
        else:
            # Default live scorecard & situation summary
            ans = (
                f"{state['batting_team']} are {state['score']} in {state['overs']} overs (CRR {state['current_run_rate']}) against {state['bowling_team']}. "
                f"{state['striker']['name']} is on {state['striker']['runs']}* ({state['striker']['balls']}b) and {state['bowler']['name']} has {state['bowler']['wickets']}-{state['bowler']['runs_conceded']}."
            )

        return {
            "match_id": match_id,
            "seq_index": seq,
            "question": q,
            "answer": ans,
            "tools_called": tools_called,
            "latency_seconds": round(time.perf_counter() - t0, 4),
        }
