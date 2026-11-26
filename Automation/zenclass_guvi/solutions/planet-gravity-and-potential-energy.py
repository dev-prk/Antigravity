import sys
from decimal import Decimal, getcontext, ROUND_HALF_UP

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    try:
        K = int(next(it))
    except StopIteration:
        return

    # sufficient precision for division
    getcontext().prec = 28

    gravity = {}
    for _ in range(K):
        try:
            name = next(it)
            g_val = Decimal(next(it))
        except StopIteration:
            break
        gravity[name] = g_val

    try:
        Q = int(next(it))
    except StopIteration:
        Q = 0

    out = []
    quant = Decimal('0.01')
    for _ in range(Q):
        try:
            U = Decimal(next(it))
            planet = next(it)
            h = Decimal(next(it))
        except StopIteration:
            break
        g = gravity.get(planet, Decimal('0'))
        if g == 0 or h == 0:
            mass = Decimal('0')
        else:
            mass = (U / (g * h)).quantize(quant, rounding=ROUND_HALF_UP)
        out.append(f"{mass:.2f}")

    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    solve()
