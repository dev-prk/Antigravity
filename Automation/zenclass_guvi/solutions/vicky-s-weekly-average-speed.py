import sys
import re

def main():
    line = sys.stdin.read().strip()
    
    if not line:
        print(-1)
        return
    
    # Extract all floating point numbers from the input
    # This handles both space-separated and + separated formats
    pattern = r'(\d+\.?\d*)'
    matches = re.findall(pattern, line)
    
    if not matches:
        print(-1)
        return
    
    try:
        speeds = [float(m) for m in matches]
    except ValueError:
        print(-1)
        return
    
    if not speeds:
        print(-1)
        return
    
    avg = sum(speeds) / len(speeds)
    print("{:.2f}".format(avg))

if __name__ == "__main__":
    main()
