import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    R = int(data[0])
    if R <= 0:
        return
    start = ord('A') + R - 1
    lines = []
    for i in range(R):
        count = R - i
        row = ''.join(chr(start - j) for j in range(count))
        lines.append(row)
    sys.stdout.write('\n'.join(lines) + '\n')

main()
