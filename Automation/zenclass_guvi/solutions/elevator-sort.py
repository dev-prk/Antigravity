import sys

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    start_floor = int(data[1])
    arr = list(map(int, data[2:2+n]))
    
    if n == 0:
        print("not possible")
        return
    
    sorted_arr = sorted(arr)
    
    # Try to find a valid arrangement
    found = False
    result = []
    
    # We need to place elements at odd indices (0-indexed: 1, 3, 5, ...) that move UP
    # and elements at even indices (0-indexed: 0, 2, 4, ...) that move DOWN
    
    # Strategy: Try to construct a valid sequence
    # Let's try using the sorted array and check if we can arrange it
    # to end at a different floor
    
    # For n elements, positions 0, 2, 4, ... (even indices) are DOWN moves
    # positions 1, 3, 5, ... (odd indices) are UP moves
    
    # We need at least one DOWN move and at least one UP move for the condition to make sense
    # But actually, let's think differently
    
    # The problem says: we need to SORT the array such that
    # the final floor is different from start_floor
    
    # Let's try different arrangements by permuting elements
    # We need to place "downs" at even positions and "ups" at odd positions
    
    # Actually, looking at the example:
    # Input: 5 8, array: 5 8 1 3 4
    # Output: 1 3 4 5 8
    # Sequence: down(1), up(3), down(4), up(5), down(8)
    # 8 - 1 + 3 - 4 + 5 - 8 = 3 (not equal to 8)
    
    # So position 0, 2, 4 are DOWN (even indices)
    # position 1, 3 are UP (odd indices)
    
    # Let's try a greedy approach
    # Put small numbers at DOWN positions and large numbers at UP positions
    # or vice versa
    
    # For the sequence to end at a different floor, we need:
    # start + (sum of ups) - (sum of downs) != start
    # which means: sum of ups != sum of downs
    
    # Let's try to find any arrangement where sum(ups) != sum(downs)
    # and all intermediate floors are valid (positive)
    
    def check_and_simulate(arrangement):
        current = start_floor
        for i in range(len(arrangement)):
            if i % 2 == 0:  # even index, DOWN
                current -= arrangement[i]
            else:  # odd index, UP
                current += arrangement[i]
            if current < 1:  # floor must be positive
                return None
        return current
    
    # Try different arrangements
    # Strategy: sort and try placing strategically
    from itertools import permutations
    
    for perm in permutations(sorted_arr):
        final = check_and_simulate(perm)
        if final is not None and final != start_floor:
            found = True
            result = list(perm)
            break
    
    if found:
        print(' '.join(map(str, result)))
    else:
        print("not possible")

if __name__ == "__main__":
    solve()
