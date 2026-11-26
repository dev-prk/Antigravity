import sys, math

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    try:
        N = int(data[0])
        K = int(data[1])
    except ValueError:
        return
    if N < 0 or K < 0 or K > N:
        print(0)
    else:
        print(math.comb(N, K))

if __name__ == "__main__":
    main()
