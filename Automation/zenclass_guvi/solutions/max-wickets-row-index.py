import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    counts = []
    # Process exactly 5 rows; if fewer, pad with zeros
    for i in range(5):
        if i < len(data):
            tokens = data[i].split()
        else:
            tokens = []
        w_count = tokens.count('W')
        counts.append(w_count)
    
    max_w = max(counts) if counts else 0
    # Row indices are 1-indexed
    result_rows = [str(i + 1) for i, c in enumerate(counts) if c == max_w]
    # Output each row index on a new line
    sys.stdout.write('\n'.join(result_rows) + '\n')

if __name__ == "__main__":
    main()
