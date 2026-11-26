import sys

def main():
    line = sys.stdin.readline().strip()
    if '=' in line and ',' in line:
        parts = line.split(',')
        a = parts[0].split('=')[1]
        b = parts[1].split('=')[1]
        result = str(int(a) + int(b))
        print(result)

if __name__ == "__main__":
    main()
