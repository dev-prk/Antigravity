def main():
    import sys
    data = sys.stdin.read().strip().split(', ')
    if len(data) < 2:
        print(-1)
        return
    s1 = data[0]
    s2 = data[1]
    result = s1 + s2
    print(result)

if __name__ == "__main__":
    main()
