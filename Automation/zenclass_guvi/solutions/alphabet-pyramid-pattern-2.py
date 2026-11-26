import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    R = int(data[0])
    
    for i in range(1, R + 1):
        # Descending part: from chr('A' + i - 1) down to 'A'
        descending = []
        for j in range(i - 1, -1, -1):
            descending.append(chr(ord('A') + j))
        
        # Ascending part: from 'B' to chr('A' + i - 1)
        ascending = []
        for j in range(1, i):
            ascending.append(chr(ord('A') + j))
        
        # Combine both parts
        line = ''.join(descending) + ''.join(ascending)
        
        # Add leading spaces
        leading_spaces = ' ' * (R - i)
        print(leading_spaces + line)

if __name__ == "__main__":
    main()
