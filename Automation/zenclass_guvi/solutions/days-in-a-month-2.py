import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        m = int(data[0])
    except ValueError:
        print("Error")
        return

    days_in_month = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    if 1 <= m <= 12:
        print(days_in_month[m])
    else:
        print("Error")

if __name__ == "__main__":
    solve()
