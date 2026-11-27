import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        return
    n = int(line)
    # Problem: Integer range in Python is typically within -2^31 to 2^31-1
    # For this problem, 'INT' means N <= 100000
    # 'LONG' means N > 100000 (but input says 1 <= N <= 100000, so this never happens)
    # Wait, let's re-read: "print 'LONG' if it is greater"
    # This suggests there's a threshold. Looking at sample:
    # 999 -> INT, 1024217 -> LONG
    # So threshold is somewhere between 999 and 1024217
    # 1024217 is about 2^20, which is larger than typical 32-bit int range
    # But 999 is well within 32-bit int range
    # Typical 32-bit signed int max is 2^31 - 1 = 2147483647
    # 1024217 < 2147483647, so that's not it
    # Maybe threshold is at 10^6 or 2^20?
    # Let's check: 1024217 ≈ 2^20 = 1048576
    # Hmm, that doesn't match exactly either
    # Actually 1024217 is just over 1 million
    # Maybe threshold is 10^6 = 1000000?
    # 999 < 1000000 -> INT
    # 1024217 > 1000000 -> LONG
    # That seems to fit!
    
    if n <= 1000000:
        print('INT')
    else:
        print('LONG')

if __name__ == "__main__":
    main()
