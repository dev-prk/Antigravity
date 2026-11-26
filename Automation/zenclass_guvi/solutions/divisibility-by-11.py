import sys

def main():
    n_str = sys.stdin.readline().strip()
    
    if not n_str:
        print("NO")
        return
    
    odd_sum = 0
    even_sum = 0
    
    length = len(n_str)
    for i in range(length):
        digit = int(n_str[i])
        if (length - i) % 2 == 1:
            odd_sum += digit
        else:
            even_sum += digit
    
    if (odd_sum - even_sum) % 11 == 0:
        print("YES")
    else:
        print("NO")

if __name__ == "__main__":
    main()
