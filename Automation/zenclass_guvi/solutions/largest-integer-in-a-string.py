import sys
import re

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    try:
        n = int(data[0])
    except ValueError:
        n = 1
    
    lines = data[1:n+1] if len(data) > 1 else data[:1]
    
    results = []
    for s in lines:
        numbers = re.findall(r'\d+', s)
        if numbers:
            largest = max(int(num) for num in numbers)
            results.append(str(largest))
        else:
            results.append("-1")
    print('\n'.join(results))

if __name__ == "__main__":
    main()
