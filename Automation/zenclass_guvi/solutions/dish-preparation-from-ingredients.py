import sys
from collections import Counter

def solve() -> None:
    data = sys.stdin.read().splitlines()
    if not data:
        return

    # Strip each line to handle possible trailing spaces
    data = [line.strip() for line in data]

    S = data[0]
    try:
        N = int(data[1])
    except (ValueError, IndexError):
        return

    # If N is negative or zero, there are no dishes to prepare
    if N <= 0:
        return

    # Frequency of each character in the source dish
    freqS = Counter(S)

    out_lines = []
    # Process exactly N dish strings, if they exist
    for i in range(min(N, len(data) - 2)):
        A = data[2 + i]
        freqA = Counter(A)
        can_prepare = True
        for ch, cnt in freqA.items():
            if freqS.get(ch, 0) < cnt:
                can_prepare = False
                break
        out_lines.append('YES' if can_prepare else 'NO')

    sys.stdout.write('\n'.join(out_lines))

if __name__ == '__main__':
    solve()
