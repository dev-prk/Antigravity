import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    values = line.split()
    floats = [float(v) for v in values]
    formatted = [f"{f:.1f}" if f == int(f) else f"{f:g}" for f in floats]
    result = [f"{float(f):g}" for f in floats]
    for val in result:
        print(val)

if __name__ == "__main__":
    main()
