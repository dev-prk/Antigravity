import sys

def check_winner(board):
    # Check rows
    for row in board:
        if row[0] != ' ' and row[0] == row[1] == row[2]:
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] != ' ' and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] != ' ' and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] != ' ' and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    return None

# Read input
lines = sys.stdin.read().strip().split('\n')
board = [line.split() for line in lines if line.strip()]

# Check for winner
winner = check_winner(board)

if winner == 'X':
    print("Player1")
elif winner == 'O':
    print("Player2")
else:
    # Check if it's a tie (board is full with no winner)
    is_full = all(cell != ' ' for row in board for cell in row)
    if is_full:
        print("TIE")
    else:
        print("TIE")
