"""Streamlit Live Cricket Broadcast, Two-Voice AI Commentary, Text+Voice Match Chat & MLOps UI."""

from __future__ import annotations

import json
import pandas as pd
import plotly.express as px
import streamlit as st

from src.agents import CommentaryMultiAgentSystem
from src.evaluation import EVAL_REPORT_PATH, judge_commentary_line, run_full_evaluation_and_log_mlflow
from src.monitoring import record_ball_metrics, record_question_metric, render_prometheus_metrics
from src.replay_engine import MatchReplayEngine
from src.speech import SpeechPipeline

st.set_page_config(
    page_title="Autonomous Sports Commentary System",
    page_icon="🏏",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading Cricsheet SQL Warehouse, Multi-Agent Commentators & Speech Engine...")
def init_platform():
    eng = MatchReplayEngine()
    ag = CommentaryMultiAgentSystem(eng, prompt_version="v2_broadcast_grounded")
    sp = SpeechPipeline()
    if not EVAL_REPORT_PATH.exists():
        run_full_evaluation_and_log_mlflow(eng)
    eval_data = json.loads(EVAL_REPORT_PATH.read_text(encoding="utf-8"))
    return eng, ag, sp, eval_data


engine, agents, speech, eval_summary = init_platform()
matches = engine.list_matches()

st.sidebar.title("🏏 Broadcast Control")
selected_match = st.sidebar.selectbox(
    "Select Cricsheet Match",
    options=[m["match_id"] for m in matches],
    format_func=lambda mid: next(f"{m['team1']} vs {m['team2']} ({m['match_date']})" for m in matches if m["match_id"] == mid),
)
language = st.sidebar.selectbox("Commentary Language", ["English", "Hindi", "Tamil"])

total_balls = engine.total_deliveries(selected_match)
if "ball_seq" not in st.session_state or st.session_state.get("active_mid") != selected_match:
    st.session_state.active_mid = selected_match
    st.session_state.ball_seq = 1
    st.session_state.feed = []

c_b1, c_b2, c_b3 = st.sidebar.columns(3)
if c_b1.button("▶ +1 Ball", use_container_width=True):
    st.session_state.ball_seq = min(total_balls, st.session_state.ball_seq + 1)
if c_b2.button("⏩ +1 Over", use_container_width=True):
    st.session_state.ball_seq = min(total_balls, st.session_state.ball_seq + 6)
if c_b3.button("🔥 Chase", use_container_width=True):
    st.session_state.ball_seq = min(total_balls, max(1, total_balls - 18))

seq_slider = st.sidebar.slider("Jump to Delivery #", 1, total_balls, st.session_state.ball_seq)
st.session_state.ball_seq = seq_slider

comm = agents.generate_ball_commentary(selected_match, st.session_state.ball_seq, language=language)
wav_audio, ttfa = speech.synthesize_tts(comm["combined_script"], speaker="aarav", language=language)
judge = judge_commentary_line(comm)
record_ball_metrics(comm["agent_latency_seconds"], ttfa, comm["estimated_tokens"])
state = comm["state_snapshot"]
meta = state["match_meta"]

st.title("🏏 Autonomous Sports Commentary System — Live AI Broadcast & Match Chat")
st.caption(f"{meta['event_name']} • {meta['team1']} vs {meta['team2']} • {meta['venue']}, {meta['city']}")

# Live Broadcast Scorecard Banner
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric(f"{state['batting_team']} (Inn {state['innings_num']})", state["score"], f"{state['overs']} Overs")
s2.metric("Current Run Rate", f"{state['current_run_rate']} RPO", f"Target: {state['target']}" if state["target"] else "1st Innings")
s3.metric(f"🏏 {state['striker']['name']}*", f"{state['striker']['runs']} ({state['striker']['balls']})", f"SR {state['striker']['strike_rate']}")
s4.metric(f"🎯 {state['bowler']['name']}", f"{state['bowler']['wickets']}-{state['bowler']['runs_conceded']}", f"Econ {state['bowler']['economy']}")
s5.metric("Event → Audio Latency", f"{(comm['agent_latency_seconds'] + ttfa)*1000:.1f} ms", f"Judge: {judge['overall_judge_score']}/5")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎙️ Live Two-Voice Commentary & Scorecard",
    "🗣️ Text & Voice Viewer Match Chat (Q&A)",
    "🧪 MLflow Experiments & 50-Question Judge Evaluation",
    "📈 Prometheus Observability & AWS Cloud Cost",
])

with tab1:
    left, right = st.columns([3, 2])
    with left:
        st.subheader(f"Live Delivery {comm['over_ball']} — Spoken Broadcast Feed ({language})")
        st.audio(wav_audio, format="audio/wav")
        with st.container(border=True):
            st.markdown(f"**🎙️ {comm['play_by_play']['speaker']}:**  \n{comm['play_by_play']['text']}")
            st.divider()
            st.markdown(f"**📊 {comm['analyst']['speaker']}:**  \n{comm['analyst']['text']}")
            st.caption(
                f"Factual Grounding: {'✅ Verified' if judge['factual_accurate'] else '⚠️ Check'} | "
                f"Fluency: `{judge['fluency_score']}/5` | Excitement: `{judge['excitement_score']}/5` | "
                f"TTS TTFA: `{ttfa*1000:.1f} ms`"
            )

    with right:
        worm_df = pd.DataFrame(state["over_worm"])
        if not worm_df.empty:
            fig = px.line(
                worm_df,
                x="over_num",
                y="cumulative_runs",
                color="batting_team",
                markers=True,
                title="Live Over-by-Over Scoring Worm",
            )
            st.plotly_chart(fig, use_container_width=True)

        perf = engine.tool_top_performers(selected_match, st.session_state.ball_seq)
        st.markdown("##### Top Run Scorers (Match-to-Date)")
        st.dataframe(pd.DataFrame(perf["top_batters"]), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Ask the Match Stats Copilot (Text or Voice)")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        st.markdown("#### 💬 Text Question")
        preset_q = st.selectbox(
            "Sample Match Questions",
            [
                "Who is the top scorer so far?",
                "What is the current partnership?",
                "Who has taken the most wickets?",
                "What is the target or chase situation?",
                "Who is batting at the crease and what is their strike rate?",
                "Who won the toss and what did they decide?",
            ],
        )
        custom_q = st.text_input("Your Question", value=preset_q)
        if st.button("Ask via Text + Audio Reply", type="primary"):
            qa_res = agents.answer_viewer_question(selected_match, custom_q, seq_index=st.session_state.ball_seq)
            ans_wav, ans_ttfa = speech.synthesize_tts(qa_res["answer"], speaker="meera", language="English")
            record_question_metric("text")
            st.success(qa_res["answer"])
            st.audio(ans_wav, format="audio/wav")
            st.caption(f"Tools used: `{', '.join(qa_res['tools_called'])}` • Latency: `{(qa_res['latency_seconds']+ans_ttfa)*1000:.1f} ms`")

    with q_col2:
        st.markdown("#### 🎤 Voice Question (`faster-whisper` ASR → Q&A → TTS)")
        uploaded_wav = st.file_uploader("Upload Viewer Voice Question (.wav)", type=["wav"])
        if st.button("Simulate Voice Question ('Who is bowling right now and what is their economy?')"):
            sim_wav, _ = speech.synthesize_tts("Who is bowling right now and what is their economy?", speaker="viewer")
            asr_res = speech.transcribe_asr(sim_wav)
            qa_v = agents.answer_viewer_question(selected_match, asr_res["transcript"], seq_index=st.session_state.ball_seq)
            v_wav, v_ttfa = speech.synthesize_tts(qa_v["answer"], speaker="meera")
            record_question_metric("voice")
            st.info(f"**ASR Transcript (`{asr_res['engine']}`):** {asr_res['transcript']}")
            st.success(f"**Spoken Answer:** {qa_v['answer']}")
            st.audio(v_wav, format="audio/wav")
            st.caption(f"End-to-End Voice Latency: `{(asr_res['latency_seconds'] + qa_v['latency_seconds'] + v_ttfa)*1000:.1f} ms` (Target ≤ 6,000 ms)")

        if uploaded_wav is not None:
            asr_res = speech.transcribe_asr(uploaded_wav.read())
            qa_v = agents.answer_viewer_question(selected_match, asr_res["transcript"], seq_index=st.session_state.ball_seq)
            v_wav, v_ttfa = speech.synthesize_tts(qa_v["answer"], speaker="meera")
            st.info(f"**ASR Transcript:** {asr_res['transcript']}")
            st.success(qa_v["answer"])
            st.audio(v_wav, format="audio/wav")

with tab3:
    st.subheader("MLflow Experiment Tracking & Target Rubric Verification")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Factual Accuracy", f"{eval_summary['commentary_factual_accuracy']*100:.1f}%", "Target ≥ 95%")
    e2.metric("LLM-Judge Score", f"{eval_summary['llm_judge_overall']} / 5.0", "Target ≥ 4.0")
    e3.metric("50-Q&A Accuracy", f"{eval_summary['qa_50_question_accuracy']*100:.1f}%", "Target ≥ 85%")
    e4.metric("ASR Word Error Rate", f"{eval_summary['asr_word_error_rate']*100:.1f}%", "Voice Q&A")

    runs_df = pd.DataFrame(eval_summary["mlflow_runs"])
    st.dataframe(runs_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Live Prometheus Metrics Exposition & AWS Free-Tier Cost Breakdown")
    st.code(render_prometheus_metrics().decode("utf-8"), language="text")
    st.markdown(
        """
        #### Cloud Cost Per Full T20 Match Replay (AWS `ap-south-1` Estimate)
        - **EC2 (`t3.medium` spot / on-demand, shut down after 1.5h replay)**: `$0.031`
        - **Amazon S3 (raw Cricsheet JSON + Parquet + audio cache)**: `$0.002`
        - **AWS Lambda Ticker (240 invocations @ 128 MB — Free Tier)**: `$0.000`
        - **Amazon RDS `db.t4g.micro` (amortized per match / Free Tier eligible)**: `$0.009`
        - **Total Estimated Cloud Cost per Match Replay**: **`$0.042 USD` (~₹3.50 INR)**
        """
    )
