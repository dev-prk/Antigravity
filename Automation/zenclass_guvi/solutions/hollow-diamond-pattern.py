import sys

def main():
    R = int(sys.stdin.readline().strip())
    total_lines = 2 * R
    total_width = 2 * R
    
    for i in range(total_lines):
        if i < R:
            left_count = R - i
        else:
            left_count = i - R + 1
        
        if left_count == 1:
            middle_spaces = total_width - 2
            line = '*' + ' ' * middle_spaces + '*'
        else:
            middle_spaces = total_width - 2 * left_count
            line = '*' * left_count + ' ' * middle_spaces + '*' * left_count
        
        print(line)

if __name__ == "__main__":
    main()
