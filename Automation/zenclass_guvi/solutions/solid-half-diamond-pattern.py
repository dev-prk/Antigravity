import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    try:
        R = int(data[0])
    except ValueError:
        return

    if R <= 0:
        return

    out = []
    for i in range(1, R + 1):
        out.append('*' * i)
    for i in range(R - 1, 0, -1):
        out.append('*' * i)

    sys.stdout.write('\n'.join(out) + '\n')

main()
