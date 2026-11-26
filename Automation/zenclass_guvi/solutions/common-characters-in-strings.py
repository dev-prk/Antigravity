import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        print("no")
        return
    s1, s2 = data[0], data[1]
    if set(s1) & set(s2):
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
