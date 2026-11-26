import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("0:0")
        return
    
    row = int(data[0])
    col = int(data[1])
    
    if row == 0 or col == 0:
        print("0:0")
        return
    
    values = list(map(int, data[2:2 + row * col]))
    
    if not values:
        print("0:0")
        return
    
    # counts[i] = number of 1s in row i (for each course)
    counts = [0] * row
    for i in range(row):
        for j in range(col):
            idx = i * col + j
            if idx < len(values) and values[idx] == 1:
                counts[i] += 1
    
    max_count = max(counts)
    max_course = counts.index(max_count)
    
    print(f"{max_course}:{max_count}")

if __name__ == "__main__":
    main()
