import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("")
        return
    idx = 0
    n = int(data[idx])
    idx += 1
    rolls = []
    for i in range(n):
        rolls.append(int(data[idx]))
        idx += 1
    marks = []
    for i in range(n):
        marks.append(int(data[idx]))
        idx += 1
    
    # Create list of (roll, original_index, mark)
    students = [(rolls[i], i, marks[i]) for i in range(n)]
    
    # Count swaps for each student using bubble sort
    swap_count = [0] * n
    
    # We need to sort by roll number, tracking swaps
    arr = [(rolls[i], i, marks[i]) for i in range(n)]
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j][0] > arr[j + 1][0]:
                # Swap the elements
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                # Count swap for both students involved
                swap_count[arr[j][1]] += 1
                swap_count[arr[j + 1][1]] += 1
    
    # Deduct marks
    result = [marks[i] - swap_count[i] for i in range(n)]
    
    print(' '.join(map(str, result)))

if __name__ == "__main__":
    main()
