import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    # Series: 3, 20, 63, 144, 275, ...
    # Let's find the pattern.
    # n=1: 3
    # n=2: 20
    # n=3: 63
    # n=4: 144
    # n=5: 275
    
    # Let's check differences:
    # 20-3 = 17
    # 63-20 = 43
    # 144-63 = 81
    # 275-144 = 131
    
    # Differences: 17, 43, 81, 131
    # Second differences:
    # 43-17 = 26
    # 81-43 = 38
    # 131-81 = 50
    # Third differences:
    # 38-26 = 12
    # 50-38 = 12
    # So the third difference is constant, meaning it's a cubic polynomial.
    # Let T(n) = an^3 + bn^2 + cn + d
    
    # We have:
    # n=1: a + b + c + d = 3
    # n=2: 8a + 4b + 2c + d = 20
    # n=3: 27a + 9b + 3c + d = 63
    # n=4: 64a + 16b + 4c + d = 144
    
    # Subtract eq1 from eq2:
    # 7a + 3b + c = 17  (E4)
    # Subtract eq2 from eq3:
    # 19a + 5b + c = 43  (E5)
    # Subtract eq3 from eq4:
    # 37a + 7b + c = 81  (E6)
    
    # Subtract E4 from E5:
    # 12a + 2b = 26  -> 6a + b = 13  (E7)
    # Subtract E5 from E6:
    # 18a + 2b = 38  -> 9a + b = 19  (E8)
    
    # Subtract E7 from E8:
    # 3a = 6 -> a = 2
    # From E7: 6(2) + b = 13 -> 12 + b = 13 -> b = 1
    # From E4: 7(2) + 3(1) + c = 17 -> 14 + 3 + c = 17 -> 17 + c = 17 -> c = 0
    # From eq1: 2(1) + 1(1) + 0 + d = 3 -> 3 + d = 3 -> d = 0
    
    # So T(n) = 2n^3 + n^2
    
    result = 2 * n**3 + n**2
    print(result)

if __name__ == "__main__":
    main()
