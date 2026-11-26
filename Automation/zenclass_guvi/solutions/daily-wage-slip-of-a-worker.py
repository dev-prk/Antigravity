import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if len(data) < 3:
        return
    rate = float(data[0])
    normal_hours = float(data[1])
    overtime_hours = float(data[2])

    normal_pay = rate * normal_hours
    overtime_pay = rate * overtime_hours * 1.5
    total_pay = normal_pay + overtime_pay

    out = "\n".join(f"{val:.2f}" for val in (normal_pay, overtime_pay, total_pay))
    sys.stdout.write(out)

if __name__ == "__main__":
    solve()
