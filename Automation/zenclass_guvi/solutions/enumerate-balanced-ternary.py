import sys
from itertools import product

def main():
    line = sys.stdin.readline().strip()
    
    if '=' in line:
        n = int(line.split('=')[1])
    else:
        n = int(line)
    
    if n == 0:
        return
    
    # Sort according to the expected order: T < 0 < 1
    # So we need to generate in that order
    digits = ['T', '0', '1']
    results = product(digits, repeat=n)
    results_list = [''.join(r) for r in results]
    
    for r in results_list:
        print(r)

if __name__ == "__main__":
    main()
