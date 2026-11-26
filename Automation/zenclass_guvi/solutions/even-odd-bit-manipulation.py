import sys

def main():
    n = int(sys.stdin.readline().strip())
    if n == 0:
        print(0)
        return
    
    max_bit = n.bit_length()
    result = 0
    
    for i in range(max_bit):
        if i % 2 == 0:
            target_pos = i + 1
        else:
            target_pos = i - 1
        
        if (n >> i) & 1:
            result |= (1 << target_pos)
    
    print(result)

if __name__ == "__main__":
    main()
