import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    # First 4 lines are the board
    board = []
    idx = 0
    for i in range(4):
        board.append(input_data[idx])
        idx += 1
    
    Q = int(input_data[idx])
    idx += 1
    
    # Knight moves: (dr, dc)
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                    (1, 2), (1, -2), (-1, 2), (-1, -2)]
    
    results = []
    for _ in range(Q):
        x = int(input_data[idx])
        y = int(input_data[idx + 1])
        idx += 2
        
        # Check if the square is blocked
        if board[x][y] == '#':
            results.append("-1")
        else:
            # Count reachable squares
            count = 0
            for dx, dy in knight_moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 4 and 0 <= ny < 4:
                    if board[nx][ny] != '#':
                        count += 1
            results.append(str(count))
    
    print('\n'.join(results))

if __name__ == "__main__":
    main()
