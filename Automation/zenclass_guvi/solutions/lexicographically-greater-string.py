import sys

def next_permutation(arr):
    n = len(arr)
    i = n - 2
    while i >= 0 and arr[i] >= arr[i + 1]:
        i -= 1
    if i == -1:
        return False
    j = n - 1
    while arr[j] <= arr[i]:
        j -= 1
    arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1:] = reversed(arr[i + 1:])
    return True

def main():
    s = sys.stdin.read()
    if not s:
        return
    s = s.rstrip('\n')
    # If input may contain multiple lines, consider only first line
    if '\n' in s:
        s = s.splitlines()[0]
    chars = list(s)
    if next_permutation(chars):
        sys.stdout.write(''.join(chars))
    else:
        sys.stdout.write('-1')

if __name__ == "__main__":
    main()
