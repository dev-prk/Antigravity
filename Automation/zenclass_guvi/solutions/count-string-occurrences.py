import sys

def main():
    # Read all input and split into lines
    lines = sys.stdin.read().splitlines()
    
    if len(lines) < 2:
        print(-1)
        return
    
    sentence = lines[0]
    target = lines[1]
    
    # Handle empty target string
    if not target:
        print(-1)
        return
    
    count = 0
    start = 0
    target_len = len(target)
    
    # Find all occurrences of target in sentence
    while True:
        idx = sentence.find(target, start)
        if idx == -1:
            break
        count += 1
        start = idx + 1  # Allow overlapping matches
    
    if count == 0:
        print(-1)
    else:
        print(count)

if __name__ == "__main__":
    main()
