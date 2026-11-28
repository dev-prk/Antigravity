import sys

def main(n):
    for i in range(n, 0, -1):
        digit = i % 2
        line = str(digit) * i
        print(line + " ")

if __name__ == "__main__":
    data = sys.stdin.read().strip()
    if data:
        try:
            n = int(float(data))
            if n > 0:
                main(n)
        except ValueError:
            pass
