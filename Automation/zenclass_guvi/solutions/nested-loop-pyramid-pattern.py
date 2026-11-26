def main():
    import sys
    n = int(sys.stdin.readline().strip())
    for i in range(1, n + 1):
        if i % 2 == 1:
            print('*' * i)
        else:
            print('#' * i)

if __name__ == "__main__":
    main()
