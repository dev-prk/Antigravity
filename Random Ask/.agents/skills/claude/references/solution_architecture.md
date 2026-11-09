# Solution Architecture, Agentic Harness & Code Craftsmanship

## 1. Architectural Philosophy: The Lean Agentic Harness

### 1.1 "Lean on the Model, Strip Down the Harness"
In foundational research on autonomous systems (*Schluntz & Zhang, "Building Effective Agents," Anthropic, November 2024*), Anthropic established that modern cognitive models thrive on simplicity rather than complex, rigid agentic frameworks. The core thesis is straightforward:

> *"Lean heavily on the cognitive capabilities of the model and aggressively strip down the surrounding agentic harness to minimal, transparent primitives."*

Over-engineered multi-agent frameworks, dense state graphs, and brittle orchestration libraries create combinatorial failure modes, compound latency, and obscure errors. High-performing engineering agents rely on disciplined, modular architectures driven by clear contracts.

### 1.2 Stateless Reasoning Core vs. Stateful Host Harness
Claude enforces an absolute architectural boundary between the reasoning engine and the operational environment:
- **Stateless Reasoning Core**: The model itself, evaluated autoregressively turn by turn. It maintains no hidden state, no mutable global variables, and no implicit memory outside the explicit token transcript.
- **Stateful Host Harness**: The surrounding runtime environment. It manages file system access, terminal execution, credential isolation, token compaction, and external network interactions.

### 1.3 Universal Primitives: The Shell and the File System
Rather than creating dozens of bespoke, fragile domain tools, the lean harness provides two universal, battle-tested abstractions:
1. **The UNIX Shell (`run_command`)**: Complete, unconstrained access to system utilities, build tools (`pytest`, `cargo`, `npm`), git versioning, and environment diagnostics.
2. **The File Editor (`view_file`, `replace_file_content`, `write_to_file`)**: Surgical read and mutation operations across the repository tree.

---

## 2. Tool Concurrency & State Mutation Contracts

### 2.1 Concurrency Rules: Read vs. Write Queues
To maintain strict data integrity and prevent race conditions, tool operations are classified into two disjoint execution queues:

$$\text{Tool Concurrency} = \begin{cases} \text{Parallel Read Queue}: & \{\text{grep\_search}, \text{find\_by\_name}, \text{view\_file}, \text{list\_dir}\} \\ \text{Serialized Mutation Queue}: & \{\text{replace\_file\_content}, \text{write\_to\_file}, \text{run\_command}\} \end{cases}$$

- **Parallel Read Queue**: Read-only diagnostic tools produce zero side-effects. They can and should be executed concurrently in batches to accelerate context discovery.
- **Serialized Mutation Queue**: Any tool that alters file system state or executes processes with potential side-effects must execute sequentially. Running mutations in parallel risks race conditions, conflicting diffs, and verification against corrupted state.

---

## 3. Context Engineering & Memory Externalization

### 3.1 Context Entropy & Attention Dilution
As conversational context fills beyond 70% capacity, transformer self-attention heads experience attention dilution. Key technical invariants declared early in the context can be neglected as new tokens accumulate.

### 3.2 Surgical AST-Level Code Modifications
To preserve context headroom and eliminate regressions:
- Always prefer surgical search-and-replace edits (`replace_file_content`) over whole-file rewrites (`write_to_file`).
- Modifying a 15-line function via `replace_file_content` consumes ~150 tokens, whereas rewriting an 800-line file consumes ~4,000 tokens. Surgical editing preserves context space by over 90% and eliminates the risk of accidentally truncating code.

### 3.3 Disk-Persisted Repository Memory
Do not attempt to maintain complex evolving state solely within conversational memory. Externalize persistent knowledge to structured files in the workspace:
- `CLAUDE.md`: Repository standards, build commands, architecture patterns, and naming conventions.
- `progress.md`: Living task state, completed milestones, pending items, and heartbeat timestamps.

---

## 4. The 5-Stage Progressive Elaboration Lifecycle

Claude approaches software engineering through a disciplined 5-stage progressive elaboration methodology:

```
┌─────────────────────────────────────────────────────────────────────────┐
│              5-STAGE PROGRESSIVE ELABORATION LIFECYCLE                  │
├─────────────────────────────────────────────────────────────────────────┤
│ Stage 1: Domain Boundary Definition & Entity Modeling                   │
│          - Define bounded contexts, aggregates, and value boundaries.   │
├─────────────────────────────────────────────────────────────────────────┤
│ Stage 2: Contract-First Typed Interface Design                          │
│          - Establish DTOs, value objects, and typing.Protocol ports.    │
├─────────────────────────────────────────────────────────────────────────┤
│ Stage 3: Core Domain Algorithm Implementation                           │
│          - Implement pure, side-effect-free business logic.             │
├─────────────────────────────────────────────────────────────────────────┤
│ Stage 4: Infrastructure Adapters & Network Boundaries                   │
│          - Implement storage repositories, HTTP gateways, and queues.   │
├─────────────────────────────────────────────────────────────────────────┤
│ Stage 5: Defensive Wrappers, Circuit Breakers & Observability           │
│          - Apply timeouts, exponential retries, and structured metrics. │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Strong Type Boundaries & Contract-First Principles

### 5.1 Prohibition of Untyped Dictionaries and Generic Any
Internal service communication must never rely on untyped dictionaries (`data: dict`) or generic `typing.Any` blobs. Untyped payloads obscure invariants, bypass IDE static analysis, and invite runtime `KeyError` exceptions.

### 5.2 Immutable Value Objects & Post-Init Validation
Domain entities must use frozen dataclasses or immutable schemas with post-initialization invariant validation. Monetary amounts, timestamps, and identifiers must never be represented as raw primitive integers or strings.

### 5.3 Production-Grade Architecture Exemplar (Python)

```python
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import NewType, Protocol, Sequence


# Strongly typed domain identifier
AccountId = NewType("AccountId", str)
TransactionId = NewType("TransactionId", str)


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class DomainError(Exception):
    """Base domain business invariant violation."""
    pass


class InsufficientFundsError(DomainError):
    pass


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0.00"):
            raise DomainError(f"Monetary amount cannot be negative: {self.amount}")

    @property
    def cents(self) -> int:
        return int((self.amount * 100).to_integral_value())

    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise DomainError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise DomainError(f"Currency mismatch: {self.currency} vs {other.currency}")
        if other.amount > self.amount:
            raise InsufficientFundsError(f"Cannot subtract {other.amount} from {self.amount}")
        return Money(amount=self.amount - other.amount, currency=self.currency)


# Contract-First Port Protocol
class AccountRepository(Protocol):
    def get_balance(self, account_id: AccountId) -> Money:
        """Retrieves verified balance from persistent storage."""
        ...

    def record_transfer(
        self,
        source: AccountId,
        destination: AccountId,
        amount: Money,
        transaction_id: TransactionId,
    ) -> None:
        """Atomically records double-entry transfer."""
        ...
```

---

## 6. The 3-Tier Error Handling Taxonomy

Production architectures must categorize failures into three orthogonal tiers with deterministic handling strategies:

### Tier 1: Domain Business Invariant Violations (Non-Retryable)
- **Examples**: `InsufficientFundsError`, `InvalidAccountStatusError`, `ItemOutOfStockError`.
- **Characteristics**: Predictable business logic failures arising from valid client requests.
- **Handling**: Catch at domain boundary, return typed error response to caller, and NEVER retry automatically.

### Tier 2: Transient Operational Failures (Retryable with Backoff)
- **Examples**: `DatabaseConnectionTimeout`, `HTTP 429 Too Many Requests`, `NetworkPartitionError`.
- **Characteristics**: Temporary infrastructure or network faults.
- **Handling**: Execute automated retry with exponential backoff and randomized jitter:
  $$t_{\text{wait}} = \min(t_{\text{max}},\, t_{\text{base}} \times 2^{\text{attempt}}) \pm \text{jitter}$$
  Trip a circuit breaker after $N$ consecutive failures to protect downstream services from cascading collapse.

### Tier 3: Fatal System Invariant Violations (Fail-Fast & Rollback)
- **Examples**: `StorageCorruptionError`, `CryptographicSignatureMismatch`, `ConfigurationStateViolation`.
- **Characteristics**: Irrecoverable violations of fundamental operational assumptions.
- **Handling**: Fail fast immediately, roll back active transactions, emit critical alerts to observability channels, and terminate the affected task safely.

---

## 7. Production Craftsmanship & Zero-Stub Policy

### 7.1 The Absolute Prohibition on Stubs
You must NEVER emit incomplete, placeholder-ridden code:
- Strictly forbidden: `// TODO: implement later`, `# pass`, `# logic goes here`, or `...` inside concrete method bodies.
- Every function, method, and endpoint included in a code solution must be fully realized with complete logic, validation, and error handling.

### 7.2 Explicit NotImplementedError Fallbacks
When an abstract base class or protocol intentionally leaves an extension hook for future concrete subclasses, do not use a bare `pass`. Explicitly raise `NotImplementedError` with a clear docstring:

```python
def execute_custom_strategy(self, payload: bytes) -> bytes:
    """Extension hook for specialized compression algorithms. Subclasses must override."""
    raise NotImplementedError("Subclasses must implement execute_custom_strategy")
```

### 7.3 Deterministic Verification Interlocks
Never declare code complete until it passes three deterministic verification gates:
1. **Syntax & AST Validity**: Clean compilation with zero syntax errors.
2. **Type Checking**: Zero type violations under strict static type checking (`mypy --strict`, `tsc`).
3. **Automated Test Suite**: 100% test pass under the project's test command (`pytest`, `cargo test`).
