# Zen Class Pending Module Assessments — Quick Study & Revision Sheet

> **Why these 5 items were not auto-submitted**: Under `/guvi-autopilot` Section 7 and academic-integrity rules, graded `Attend` assessments (`Mod11`–`Mod15`) require your own unaided performance (`CCT_Regular` is closed and already superseded by your completed `RE CCT` score of **96/100**, and `Active Tasks` has **0** coding/GitHub tasks). Below is a concise revision sheet mapped to your 5 remaining modules (`Deadline: 28.02.27`).

---

## 1. `Mod11_RAG` — Retrieval-Augmented Generation (`Intel_AIML_RAG`)
- **Pipeline Stages**: Ingestion -> Chunking (`RecursiveCharacterTextSplitter`, fixed-token with overlap ~10–20%) -> Embedding (`BGE`, `E5`, `MiniLM`, `text-embedding`) -> Vector Index (`FAISS` `IndexFlatIP`/`IndexHNSWFlat`, `Chroma`, `Milvus`, `Qdrant`) -> Retrieval -> Reranking (Cross-Encoder / `BGE-Reranker`) -> Grounded Generation.
- **Similarity Metrics**: Cosine similarity ($\frac{A \cdot B}{\|A\|\|B\|}$; equivalent to inner product `IndexFlatIP` when L2-normalized), Euclidean distance (`IndexFlatL2`), Dot product.
- **Hybrid Search & Fusion**: Dense (semantic embeddings) + Sparse (`BM25` exact keyword match) merged via **Reciprocal Rank Fusion (RRF)**: $\text{RRF}(d) = \sum_r \frac{1}{k + \text{rank}_r(d)}$ ($k \approx 60$).
- **RAG Evaluation (RAGAS Triad)**:
  - **Context Precision / Recall**: Did the retriever fetch relevant ground-truth chunks?
  - **Faithfulness (Groundedness)**: Are all claims in the answer supported by retrieved context (measures hallucination)?
  - **Answer Relevance**: Does the generated answer address the user's query?

---

## 2. `Mod12_AGAI` — Agentic AI (`Intel_AIML_AgenticAI`)
- **Core Loop (`ReAct`)**: `Thought -> Action (Tool Call) -> Observation -> ... -> Final Answer`.
- **Design Patterns**:
  - **Reflection / Self-Critique**: Generator + Critic loop iteratively improving output.
  - **Tool Use / Function Calling**: Structured JSON schema arguments validated before execution.
  - **Planning**: Plan-and-Execute, Tree-of-Thoughts, DAG task decomposition.
  - **Multi-Agent Orchestration**: Supervisor/Router pattern (`LangGraph` stateful graph nodes + conditional edges, `CrewAI` role-based crews, `AutoGen` conversational agents).
- **Memory Types**: Short-term (conversation/working state in context window), Long-term episodic/semantic (vector store), Procedural (system prompts/playbooks).

---

## 3. `Mod13_FITu` — LLM Fine-Tuning & Optimization (`Intel_AIML_LLM_FineTuning`)
- **Full Fine-Tuning vs PEFT**: Full updates 100% of weights (high VRAM for optimizer states + gradients); **PEFT** freezes base weights $W_0 \in \mathbb{R}^{d \times k}$ and trains <1–2% parameters.
- **LoRA**: $\Delta W = B A$ where $B \in \mathbb{R}^{d \times r}, A \in \mathbb{R}^{r \times k}, r \ll \min(d, k)$; scaled by $\frac{\alpha}{r}$. Zero extra inference latency once merged ($W = W_0 + \frac{\alpha}{r}BA$).
- **QLoRA**: 4-bit **NormalFloat (`NF4`)** quantized frozen base model + **Double Quantization** (quantizing quantization constants) + **Paged Optimizers** (CPU offloading on VRAM spikes), computing forward/backward in `bfloat16`.
- **Instruction Tuning (`SFT`)**: Formats (`ChatML`, `Alpaca`), loss masking on prompt tokens (cross-entropy computed only on assistant completion tokens).
- **Inference Quantization (Intel AI PC / Edge)**: `OpenVINO` (`INT8`/`INT4` weight compression), `GGUF`, `AWQ`, `GPTQ`.

---

## 4. `Mod14_RL` — Reinforcement Learning & Alignment (`Intel Reinforcement Learning`)
- **MDP Tuple**: $(S, A, P, R, \gamma)$; Return $G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}$.
- **Value vs Policy Methods**:
  - **Q-Learning (Off-policy TD)**: $Q(s,a) \leftarrow Q(s,a) + \alpha [r + \gamma \max_{a'} Q(s',a') - Q(s,a)]$.
  - **SARSA (On-policy TD)**: Uses actual next action $Q(s', a')$ instead of $\max_{a'}$.
  - **DQN**: Experience Replay buffer (breaks correlation) + Target Network (stabilizes TD targets).
  - **Policy Gradient (`REINFORCE`, `Actor-Critic`, `PPO`)**: **PPO** clips probability ratio $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ to $[1-\epsilon, 1+\epsilon]$ to prevent destructive policy updates.
- **LLM Alignment**:
  - **RLHF**: SFT -> Reward Model (Bradley-Terry pairwise preference loss) -> PPO with KL-divergence penalty $\beta D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})$ to prevent reward hacking.
  - **DPO (Direct Preference Optimization)**: Optimizes policy directly on $(x, y_w, y_l)$ preference pairs without training a separate reward model.
  - **GRPO**: Group Relative Policy Optimization — estimates advantage from group-sampled outputs without a separate critic network.

---

## 5. `Mod15_MLop` — MLOps + LLMOps (`Intel_MLOps+MMLOps`)
- **Experiment & Model Lifecycle**: `MLflow` (Tracking parameters/metrics/artifacts, Model Registry staging -> production), `DVC` (data & pipeline versioning).
- **Containerization & Serving**: `Docker` multi-stage builds, `FastAPI` / `Triton` / `vLLM` (PagedAttention + continuous batching for high-throughput LLM serving), `Kubernetes` HPA autoscaling.
- **CI/CD/CT**: Continuous Integration (unit + data schema tests), Continuous Delivery (canary / blue-green / shadow deployment), Continuous Training (triggered by drift).
- **Monitoring & Drift**:
  - **Data / Covariate Drift**: Input feature distribution $P(X)$ shifts (measured via **PSI — Population Stability Index**, KS-test, KL/JS divergence; $\text{PSI} > 0.2$ indicates significant drift).
  - **Concept Drift**: Relationship $P(Y|X)$ changes over time (accuracy/F1 drops even if $P(X)$ looks stable).
  - **LLMOps Observability**: Token latency (**TTFT** — Time To First Token, **TPOT** — Time Per Output Token), prompt-injection guardrails, tracing (`OpenTelemetry`, `Arize Phoenix`, `Langfuse`).
