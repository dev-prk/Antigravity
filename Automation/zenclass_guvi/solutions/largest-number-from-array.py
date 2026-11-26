def main():
    import sys
    n = int(sys.stdin.readline().strip())
    arr = sys.stdin.readline().strip().split()
    arr = [x for x in arr if x]
    if len(arr) == 0:
        print(-1)
        return
    arr.sort(key=lambda x: x*10, reverse=True)
    result = ''.join(arr)
    print(result)

if __name__ == "__main__":
    main()
