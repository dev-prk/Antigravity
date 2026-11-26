import sys

def main():
    line = sys.stdin.readline().strip()
    if '=' in line:
        m = int(line.split('=')[1])
    else:
        m = int(line)
    
    if m <= 0:
        print("Period: -1")
        return
    
    if m == 1:
        print("Period: 1")
        print("Sequence: 0")
        return
    
    prev, curr = 0, 1
    period = 0
    sequence = [0, 1]
    
    for i in range(2, m * m + 1):
        prev, curr = curr, (prev + curr) % m
        sequence.append(curr)
        period += 1
        
        if prev == 0 and curr == 1:
            break
    
    # The period is the length of the sequence minus 2 (excluding initial 0, 1)
    period = len(sequence) - 2
    
    print(f"Period: {period}")
    print("Sequence: " + " ".join(map(str, sequence[:-2])))

if __name__ == "__main__":
    main()
