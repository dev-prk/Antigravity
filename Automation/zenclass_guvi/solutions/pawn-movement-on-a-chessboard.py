import sys

def main():
    board = []
    for _ in range(4):
        line = sys.stdin.readline().strip()
        board.append(line)
    
    q = int(sys.stdin.readline().strip())
    
    results = []
    for _ in range(q):
        line = sys.stdin.readline().strip()
        x, y = map(int, line.split())
        
        if board[x][y] == '#':
            results.append(-1)
        else:
            count = 0
            if x > 0 and board[x-1][y] == '.':
                count += 1
            results.append(count)
    
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
