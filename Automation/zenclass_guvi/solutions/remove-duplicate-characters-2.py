import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    parts = [p.strip() for p in line.split('->') if p.strip() != '']
    seen = set()
    out = []
    for ch in parts:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    print('->'.join(out))

if __name__ == "__main__":
    main()
