import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print("no")
        return
    
    n = int(data[0].strip())
    if n == 0:
        print("yes")
        return
    
    vowels = set('aeiouAEIOU')
    
    for i in range(1, n + 1):
        if i >= len(data):
            print("no")
            return
        s = data[i].strip()
        if not any(char in vowels for char in s):
            print("no")
            return
    
    print("yes")

if __name__ == "__main__":
    main()
