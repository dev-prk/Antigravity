import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    n_line = data[0].strip()
    if not n_line:
        return
    try:
        n = int(n_line)
    except ValueError:
        # if first line not an integer, treat whole input as list line
        n = 0
    if len(data) < 2:
        tokens = []
    else:
        tokens = data[1].split()
    seen = set()
    result = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            result.append(token)
    print(' '.join(result))

if __name__ == "__main__":
    main()
