import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    s = line
    # Remove any non-binary characters, but problem says only 0s and 1s
    # Convert binary string to integer
    if s == '' or all(c == '0' for c in s):
        print("0")
        return
    n = int(s, 2)
    hex_str = hex(n)[2:]
    print(hex_str)

if __name__ == "__main__":
    main()
