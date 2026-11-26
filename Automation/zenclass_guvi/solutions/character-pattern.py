import sys

def main():
    R = int(sys.stdin.readline().strip())
    mid = R // 2
    
    for i in range(R):
        if i <= mid:
            row = i
        else:
            row = R - 1 - i
        
        b_count = mid - row
        star_count = 2 * row + 1
        
        line = 'b' * b_count + '*' * star_count + 'b' * b_count
        print(line)

if __name__ == "__main__":
    main()
