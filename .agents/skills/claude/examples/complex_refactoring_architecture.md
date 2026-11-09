# Exemplar: Monolith-to-Modular Architecture Refactoring

This exemplar demonstrates Claude's software engineering discipline: decomposing a coupled monolithic procedural routine into clean, decoupled domain modules, typed DTOs, interface protocols, and resilient error boundaries, delivered with strict post-code restraint.

---

## User Prompt

Refactor this tightly coupled monolithic Python order processing function into a modular, production-grade service architecture:

```python
def process_order(order_data, db_conn, stripe_client, sendgrid_client):
    # Monolithic procedural blob
    if not order_data.get("items"):
        raise Exception("No items")
    total = sum(i["price"] * i["qty"] for i in order_data["items"])
    if order_data.get("discount_code") == "SAVE10":
        total *= 0.90
    # Direct DB mutation
    cursor = db_conn.cursor()
    for item in order_data["items"]:
        cursor.execute("UPDATE stock SET qty = qty - %s WHERE item_id = %s", (item["qty"], item["id"]))
    # Stripe call
    charge = stripe_client.charges.create(amount=int(total * 100), currency="usd", customer=order_data["customer_id"])
    cursor.execute("INSERT INTO orders (id, total, status) VALUES (%s, %s, %s)", (charge.id, total, "PAID"))
    db_conn.commit()
    # Email
    sendgrid_client.send_email(to=order_data["email"], subject="Order Confirmed", body=f"Charged {total}")
    return {"order_id": charge.id, "status": "PAID"}
```

Requirements:
1. Strangler pattern / clean domain boundaries (Order, Payment, Inventory, Notification).
2. Typed DTOs with immutable value objects.
3. Explicit interface boundaries (`typing.Protocol`).
4. 3-tier error handling hierarchy (Domain, Infrastructure, Transient).
5. Do NOT provide an unsolicited conversational tutorial or breakdown after the code; just deliver the clean architecture.

---

## Assistant Response

<claude_thinking>
[PHASE 1: CONSTRAINT ANCHORING & PROBLEM DECONSTRUCTION]
Quoting user constraints verbatim:
- "Strangler pattern / clean domain boundaries (Order, Payment, Inventory, Notification)."
- "Typed DTOs with immutable value objects."
- "Explicit interface boundaries (typing.Protocol)."
- "3-tier error handling hierarchy (Domain, Infrastructure, Transient)."
- "Do NOT provide an unsolicited conversational tutorial or breakdown after the code; just deliver the clean architecture."

Deficiencies of original monolithic code:
- Untyped dictionaries (`order_data["items"]`).
- Distributed transaction failure: If Stripe succeeds but DB commit fails, money is charged with zero order record.
- Lack of rollback: If inventory check fails midway, previous items remain decremented.
- Tight coupling: Directly bound to concrete `stripe_client`, `sendgrid_client`, raw SQL cursors.
- Generic exception raising (`raise Exception("No items")`).

[PHASE 2: HYPOTHESIS EXPLORATION & COUNTER-FACTUAL STRESS TESTING]
Decomposition strategy:
- Architecture: Clean Architecture / Ports and Adapters.
- Domain Entities & Value Objects:
  * `Money`: Immutable value object preventing float precision errors (using integer cents or Decimal).
  * `OrderItem`: Frozen dataclass.
  * `Order`: Encapsulates items, customer id, status.
- Interfaces (Protocols):
  * `PaymentGateway`: `charge(order_id, amount, customer_id, idempotency_key) -> PaymentReceipt`
  * `InventoryRepository`: `reserve(items) -> ReservationToken`, `release(token)`
  * `OrderRepository`: `save(order) -> None`
  * `NotificationService`: `send_confirmation(email, order) -> None`
- 3-Tier Error Hierarchy:
  * Tier 1: `AppError` (Base)
  * Tier 2: `DomainValidationError` (Client-recoverable, invalid business rules)
  * Tier 3: `InfrastructureError` (Storage/Third-party failures)
    - Subtype: `TransientInfrastructureError` (Network timeout, 503, retryable with backoff)
- Failure Isolation / Compensation:
  * Sequence: 1. Validate Order -> 2. Reserve Inventory -> 3. Charge Payment (with Idempotency Key) -> 4. Persist Order -> 5. Async Notify.
  * Compensation hook: If Payment fails, immediately release inventory reservation.

[PHASE 3: ARCHITECTURAL BLUEPRINTING & CODE VERIFICATION]
- Write complete, robust, self-contained Python code.
- Must be 100% syntactically valid Python parseable by `ast.parse`.
- Absolutely no placeholder stubs (`# TODO`, `pass` without implementation).

[PHASE 4: OUTPUT CALIBRATION & RESTRAINT CHECK]
- Verbatim constraint check: "Do NOT provide an unsolicited conversational tutorial or breakdown after the code; just deliver the clean architecture."
- Suppression rule: Zero markdown paragraphs explaining what classes were created.
- Offer single concise follow-up sentence: "I can provide unit tests with mock adapters or database integration tests if you'd like."
</claude_thinking>

```python
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Protocol, Sequence
import uuid


# =============================================================================
# 1. Error Hierarchy (3-Tier Classification)
# =============================================================================

class AppError(Exception):
    """Base application exception."""
    pass


class DomainValidationError(AppError):
    """Tier 1: Business rule violation or invalid state (non-retryable)."""
    pass


class InfrastructureError(AppError):
    """Tier 2: External system, database, or network failure."""
    pass


class TransientInfrastructureError(InfrastructureError):
    """Tier 3: Temporary failure eligible for retry with exponential backoff."""
    pass


# =============================================================================
# 2. Domain Models & Immutable Value Objects
# =============================================================================

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.amount < Decimal("0.00"):
            raise DomainValidationError(f"Monetary amount cannot be negative: {self.amount}")

    @property
    def cents(self) -> int:
        return int((self.amount * 100).to_integral_value())

    def apply_discount_percentage(self, percent: Decimal) -> Money:
        if not (Decimal("0") <= percent <= Decimal("100")):
            raise DomainValidationError(f"Invalid discount percentage: {percent}")
        discounted = self.amount * (Decimal("1") - (percent / Decimal("100")))
        return Money(amount=discounted.quantize(Decimal("0.01")), currency=self.currency)


@dataclass(frozen=True)
class OrderItem:
    item_id: str
    quantity: int
    unit_price: Money

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise DomainValidationError(f"Item quantity must be positive, got {self.quantity}")

    @property
    def subtotal(self) -> Money:
        total_amount = self.unit_price.amount * Decimal(self.quantity)
        return Money(amount=total_amount, currency=self.unit_price.currency)


@dataclass
class Order:
    id: str
    customer_id: str
    email: str
    items: Sequence[OrderItem]
    discount_code: str | None = None
    status: OrderStatus = OrderStatus.PENDING
    payment_reference: str | None = None

    def calculate_total(self) -> Money:
        if not self.items:
            raise DomainValidationError("Cannot process an order with zero items")
        raw_total = sum((item.subtotal.amount for item in self.items), Decimal("0.00"))
        total_money = Money(amount=raw_total, currency=self.items[0].unit_price.currency)
        if self.discount_code == "SAVE10":
            return total_money.apply_discount_percentage(Decimal("10"))
        return total_money


@dataclass(frozen=True)
class PaymentReceipt:
    transaction_id: str
    amount_charged: Money
    idempotency_key: str


@dataclass(frozen=True)
class InventoryReservation:
    reservation_id: str
    items: Sequence[OrderItem]


# =============================================================================
# 3. Port Protocols (Decoupled Boundaries)
# =============================================================================

class PaymentGateway(Protocol):
    def charge(
        self,
        customer_id: str,
        amount: Money,
        idempotency_key: str
    ) -> PaymentReceipt:
        """Charges customer account. Raises TransientInfrastructureError or InfrastructureError."""
        ...


class InventoryRepository(Protocol):
    def reserve_stock(self, items: Sequence[OrderItem]) -> InventoryReservation:
        """Reserves inventory items. Raises DomainValidationError if out of stock."""
        ...

    def release_reservation(self, reservation: InventoryReservation) -> None:
        """Compensating transaction releasing reserved inventory."""
        ...


class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        """Persists order state to durable storage."""
        ...


class NotificationService(Protocol):
    def send_order_confirmation(self, email: str, order: Order) -> None:
        """Dispatches asynchronous notification to customer."""
        ...


# =============================================================================
# 4. Use Case Orchestrator (Strangler Implementation)
# =============================================================================

class ProcessOrderUseCase:
    def __init__(
        self,
        payment_gateway: PaymentGateway,
        inventory_repo: InventoryRepository,
        order_repo: OrderRepository,
        notification_service: NotificationService,
    ) -> None:
        self._payment_gateway = payment_gateway
        self._inventory_repo = inventory_repo
        self._order_repo = order_repo
        self._notification_service = notification_service

    def execute(self, order: Order) -> Order:
        total_price = order.calculate_total()
        idempotency_key = f"order-charge-{order.id}-{uuid.uuid4()}"

        # Step 1: Reserve inventory
        reservation = self._inventory_repo.reserve_stock(order.items)

        # Step 2: Attempt Payment with compensation on failure
        try:
            receipt = self._payment_gateway.charge(
                customer_id=order.customer_id,
                amount=total_price,
                idempotency_key=idempotency_key,
            )
        except Exception as exc:
            # Compensating transaction: release reserved stock
            self._inventory_repo.release_reservation(reservation)
            order.status = OrderStatus.FAILED
            self._order_repo.save(order)
            if isinstance(exc, (InfrastructureError, DomainValidationError)):
                raise exc
            raise InfrastructureError(f"Payment gateway operation failed: {exc}") from exc

        # Step 3: Update and persist order
        order.status = OrderStatus.PAID
        order.payment_reference = receipt.transaction_id
        self._order_repo.save(order)

        # Step 4: Fire-and-forget notification (non-fatal)
        try:
            self._notification_service.send_order_confirmation(order.email, order)
        except Exception:
            # Swallowed or queued to dead-letter queue; does not abort paid order
            pass

        return order
```

I can provide the unit test suite or the Postgres/Stripe adapter implementations if you'd like.
