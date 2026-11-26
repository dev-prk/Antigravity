import sys

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    R = int(data[0])
    
    # Determine the middle row for b count. Let's analyze R=10:
    # 0, 2, 4, 6, 8, 6, 4, 2, 0
    # We need to handle the number of rows. It seems to be 2*(R/2) - 1?
    # R=10 -> 9 rows. R/2 = 5. 2*5-1 = 9.
    # R=2:
    # **
    # **
    # R/2=1. 2*1-1 = 1 row? But sample isn't given for R=2.
    # Let's check the pattern generation logic derived from R=10:
    # Row 0: 8 stars, 0 b -> b count starts at 0, goes up by 2 until...
    # Max b count seems to be R - 2. For R=10, max b is 8.
    # Sequence of b counts: 0, 2, 4, 6, 8, 6, 4, 2, 0.
    # This is a pyramid shape for b's.
    # Let N be the number of "steps" up.
    # For R=10, steps up: 0, 2, 4, 6, 8 (5 values).
    # Steps down: 6, 4, 2, 0 (4 values).
    # Total rows: 9.
    
    # Let's generalize:
    # Max b = R - 2.
    # If R=2, max b = 0. Sequence: 0. Rows: 1? 
    # Pattern for R=2:
    # **
    # Is it 1 row or 2?
    # Let's look at the stars.
    # Row i has (R - b_i) stars and b_i b's.
    # Star string = ('*' * (R//2 - b_i//2)).ljust(R, 'b')? No, stars are on both sides.
    # Left stars: (R - b) // 2
    # Right stars: (R - b) // 2
    # Middle chars: b's
    
    # Let's verify with R=10, b=0:
    # (10-0)/2 = 5 stars left, 5 stars right. "*****" + "" + "*****" = "**********". Correct.
    # R=10, b=8:
    # (10-8)/2 = 1 star left, 1 star right. "*" + "bbbbbbbb" + "*" = "*bbbbbbbb*". Correct.
    
    # Number of rows:
    # The b values increase by 2 starting from 0.
    # Sequence: 0, 2, ..., max_b, max_b-2, ..., 0.
    # Max b is R-2.
    # The number of terms in the increasing part (including 0) is (R-2)/2 + 1 = R/2 - 1 + 1 = R/2.
    # The number of terms in the decreasing part (excluding max_b) is (R-2)/2 - 1 + 1 ... wait.
    # Values: 0, 2, ..., R-2. Count = (R-2)/2 + 1 = R/2.
    # Values: R-4, ..., 0. Count = (R-4)/2 + 1 = R/2 - 1.
    # Total rows = R/2 + R/2 - 1 = R - 1.
    # For R=10, rows = 9. Correct.
    
    # Generate list of b counts
    half_r = R // 2
    max_b = R - 2
    inc_part = list(range(0, max_b + 1, 2))
    dec_part = list(range(max_b - 2, -1, -2))
    b_counts = inc_part + dec_part
    
    lines = []
    for b in b_counts:
        stars_side = (R - b) // 2
        line = '*' * stars_side + 'b' * b + '*' * stars_side
        lines.append(line)
    
    sys.stdout.write('\n'.join(lines))

if __name__ == '__main__':
    solve()
