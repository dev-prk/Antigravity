def solve() -> None:
    try:
        R = int(input().strip())
    except:
        return

    total = 2 * R
    for r in range(total):
        # distance from the nearest edge of the rectangle
        i = r if r < R else total - 1 - r
        stars = R - i
        spaces = 2 * i
        line = '*' * stars + ' ' * spaces + '*' * stars
        print(line)


if __name__ == "__main__":
    solve()
