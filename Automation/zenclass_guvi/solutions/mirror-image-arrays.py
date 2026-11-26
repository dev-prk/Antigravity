import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    if n == 0:
        print("yes")
        return
    # first array
    arr1 = list(map(int, data[1:1 + n]))
    # second array
    arr2 = list(map(int, data[1 + n:1 + 2 * n]))
    # check mirror image: reversed arr1 should equal arr2
    if arr1[::-1] == arr2:
        print("yes")
    else:
        print("no")

if __name__ == "__main__":
    main()
