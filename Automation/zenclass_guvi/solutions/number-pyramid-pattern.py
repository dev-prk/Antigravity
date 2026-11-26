import sys

def main():
    line = sys.stdin.readline()
    if not line:
        return
    R = int(line.strip())
    
    for i in range(1, R + 1):
        # Leading spaces
        spaces = ' ' * (R - i)
        
        # Left part: i, i+1, ..., 2*i-1
        left_part = ''.join(str(j) for j in range(i, 2 * i))
        
        # Right part: 2*i-2, 2*i-3, ..., i (excluding the peak)
        right_part = ''.join(str(j) for j in range(2 * i - 2, i - 1, -1))
        
        # Combine all parts
        row = spaces + left_part + right_part
        print(row)

if __name__ == "__main__":
    main()
