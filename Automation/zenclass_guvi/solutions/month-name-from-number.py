import sys

def solve():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    months = [
        "", "January", "February", "March", "April",
        "May", "June", "July", "August", "September",
        "October", "November", "December"
    ]
    if 1 <= n <= 12:
        print(months[n])
    else:
        print("Invalid Month")

if __name__ == "__main__":
    solve()
