import sys
from collections import defaultdict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n = int(data[0])
    if n == 0:
        print(0)
        return
    
    recipes = data[1:n+1]
    
    groups = defaultdict(list)
    for i in range(n):
        recipe = recipes[i]
        groups[recipe].append(i + 1)
    
    unique_recipes = sorted(groups.keys())
    
    print(len(unique_recipes))
    for recipe in unique_recipes:
        indices = sorted(groups[recipe])
        print(' '.join(map(str, indices)))

if __name__ == "__main__":
    main()
