import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    m = int(data[1])
    
    if n == 0 or m == 0:
        print(0)
        return
    
    grid = []
    index = 2
    for i in range(n):
        if index < len(data):
            row = data[index].strip()
            index += 1
            if len(row) < m:
                row = row + 'R' * (m - len(row))
            grid.append(row[:m])
        else:
            grid.append('R' * m)
    
    def calculate_cost(grid, start_color):
        cost = 0
        for i in range(n):
            for j in range(m):
                if (i + j) % 2 == 0:
                    expected = start_color
                else:
                    expected = 'G' if start_color == 'R' else 'R'
                
                current = grid[i][j]
                if current != expected:
                    if current == 'R' and expected == 'G':
                        cost += 5
                    elif current == 'G' and expected == 'R':
                        cost += 3
        return cost
    
    cost1 = calculate_cost(grid, 'R')
    cost2 = calculate_cost(grid, 'G')
    
    result = min(cost1, cost2)
    print(result)

if __name__ == "__main__":
    main()
