import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    R = int(data[0])
    C = int(data[1])
    
    matrix = []
    index = 2
    for i in range(R):
        row = list(map(int, data[index:index + C]))
        matrix.append(row)
        index += C
    
    # Create double pointers (list of pointers to rows)
    row_pointers = [None] * R
    for i in range(R):
        row_pointers[i] = matrix[i]
    
    # Transpose using double pointers
    # Result has C rows and R columns
    transposed_rows = C
    transposed_cols = R
    
    for i in range(transposed_rows):
        row_ptr = [None] * transposed_cols
        for j in range(transposed_cols):
            row_ptr[j] = row_pointers[j][i]
        print(' '.join(map(str, row_ptr)))
    
    # Clear pointers (simulating freeing memory)
    for i in range(R):
        row_pointers[i] = None

if __name__ == "__main__":
    main()
