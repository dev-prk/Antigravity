import sys

def main():
    s = int(sys.stdin.readline().strip())
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    print(h)
    print(m)
    print(sec)

if __name__ == "__main__":
    main()
