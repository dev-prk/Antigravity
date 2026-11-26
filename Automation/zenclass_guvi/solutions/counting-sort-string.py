import sys

def main():
    data = sys.stdin.read().splitlines()
    n = int(data[0].strip())
    s = data[1].strip()
    
    # Counting sort for lowercase letters
    count = [0] * 26
    
    for char in s:
        count[ord(char) - ord('a')] += 1
    
    result = []
    for i in range(26):
        result.append(chr(ord('a') + i) * count[i])
    
    print(''.join(result))

if __name__ == "__main__":
    main()
