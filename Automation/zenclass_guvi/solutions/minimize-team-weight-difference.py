import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    weights = list(map(int, data[1:1+n]))
    
    weights.sort()
    
    total_sum = sum(weights)
    target = total_sum / 2
    
    best_diff = float('inf')
    min_player_diff = float('inf')
    
    team1_counts = {}
    team1_sum = 0
    
    for i in range(n + 1):
        team1_size = i
        team2_size = n - i
        player_diff = abs(team1_size - team2_size)
        
        if team1_size == 0:
            current_sum = 0
        elif team1_size == n:
            current_sum = total_sum
        else:
            current_sum = sum(weights[:team1_size])
        
        weight_diff = abs(current_sum * 2 - total_sum)
        
        if weight_diff < best_diff - 1e-9:
            best_diff = weight_diff
            min_player_diff = player_diff
        elif abs(weight_diff - best_diff) < 1e-9:
            if player_diff < min_player_diff:
                min_player_diff = player_diff
    
    print(min_player_diff)

if __name__ == "__main__":
    main()
