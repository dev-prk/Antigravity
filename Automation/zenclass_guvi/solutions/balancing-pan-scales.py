import sys

def main():
    line1 = sys.stdin.readline().rstrip('\n')
    line2 = sys.stdin.readline().rstrip('\n')
    
    pipe_pos = line1.index('|')
    left = line1[:pipe_pos]
    right = line1[pipe_pos + 1:]
    
    remaining = line2
    
    left_count = len(left)
    right_count = len(right)
    remaining_count = len(remaining)
    
    diff = left_count - right_count
    total = left_count + right_count + remaining_count
    
    if total % 2 != 0:
        print(-1)
        return
    
    needed = (diff + remaining_count) // 2
    
    if needed < 0 or needed > remaining_count:
        print(-1)
        return
    
    new_left = left + remaining[:needed]
    new_right = right + remaining[needed:]
    
    print(new_left + '|' + new_right)

if __name__ == "__main__":
    main()
