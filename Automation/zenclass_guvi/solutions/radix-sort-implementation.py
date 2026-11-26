import sys

def radix_sort(arr):
    if not arr:
        return arr
    
    # Handle negative numbers by separating them
    negatives = [x for x in arr if x < 0]
    positives = [x for x in arr if x >= 0]
    
    # Sort negatives (in reverse order, then reverse the result)
    if negatives:
        # Take absolute values for sorting
        neg_abs = [abs(x) for x in negatives]
        sorted_neg_abs = _radix_sort_positive(neg_abs)
        # Convert back to negative and reverse
        negatives = [-x for x in sorted_neg_abs[::-1]]
    
    # Sort positives
    if positives:
        positives = _radix_sort_positive(positives)
    
    return negatives + positives

def _radix_sort_positive(arr):
    if not arr:
        return arr
    
    max_val = max(arr)
    
    # Do counting sort for every digit
    exp = 1
    while max_val // exp > 0:
        _counting_sort_by_digit(arr, exp)
        exp *= 10
    
    return arr

def _counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    # Store count of occurrences in count[]
    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1
    
    # Change count[i] so that count[i] contains actual
    # position of this digit in output[]
    for i in range(1, 10):
        count[i] += count[i - 1]
    
    # Build the output array
    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
    
    # Copy the output array to arr[]
    for i in range(n):
        arr[i] = output[i]

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print()
        return
    
    arr = list(map(int, data[1:n+1]))
    result = radix_sort(arr)
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
