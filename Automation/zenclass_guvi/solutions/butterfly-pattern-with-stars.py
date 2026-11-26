import sys


def main():
    data = sys.stdin.read().split()
    if not data:
        return
    R = int(data[0])
    if R <= 0:
        return
    lines = []
    for i in range(1, R + 1):
        spaces = 2 * R - 2 * i
        lines.append('*' * i + ' ' * spaces + '*' * i)
    for i in range(R, 0, -1):
        spaces = 2 * R - 2 * i
        lines.append('*' * i + ' ' * spaces + '*' * i)
    sys.stdout.write('\n'.join(lines) + '\n')


main()
