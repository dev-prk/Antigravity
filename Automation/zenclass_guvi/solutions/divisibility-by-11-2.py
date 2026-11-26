import sys

def main():
    n = sys.stdin.readline().strip()
    
    if not n:
        print("NO")
        return
    
    alternating_sum = 0
    for i in range(len(n)):
        digit = int(n[i])
        if i % 2 == 0:
            alternating_sum += digit
        else:
            alternating_sum -= digit
    
    if alternating_sum % 11 == 0:
        print("YES")
    else:
        print("NO")

if __name__ == "__main__":
    main()
