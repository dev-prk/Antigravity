import sys
from collections import defaultdict

def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    
    if not lines:
        return
    
    bowlers = lines[:6]
    runs_data = lines[6:]
    
    runs_per_bowler = defaultdict(int)
    ball_count = 0
    
    for i in range(min(6, len(bowlers))):
        if i < len(runs_data):
            runs_line = runs_data[i]
            runs_list = [int(x) for x in runs_line.split()]
            for run in runs_list:
                runs_per_bowler[bowlers[i]] += run
                ball_count += 1
    
    if not runs_per_bowler:
        return
    
    max_runs = max(runs_per_bowler.values())
    
    results = [bowler for bowler, runs in runs_per_bowler.items() if runs == max_runs]
    results.sort()
    
    print(results[0])

if __name__ == "__main__":
    main()
