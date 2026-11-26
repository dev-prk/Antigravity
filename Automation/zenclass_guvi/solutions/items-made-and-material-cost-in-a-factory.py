import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    items_per_hour, working_hours, cost_per_item = map(int, data[:3])
    total_items = items_per_hour * working_hours
    total_cost = total_items * cost_per_item
    print(total_items)
    print(total_cost)

if __name__ == "__main__":
    solve()
