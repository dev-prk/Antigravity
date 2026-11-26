import sys

def main():
    lines = sys.stdin.read().strip().split('\n')
    if len(lines) < 2:
        print("NIL")
        return
    
    try:
        M = int(lines[0].strip())
    except:
        print("NIL")
        return
    
    elements = lines[1].strip().split()
    
    if M < 1 or M > len(elements):
        print("NIL")
        return
    
    result = elements[-M]
    print(result)

if __name__ == "__main__":
    main()
