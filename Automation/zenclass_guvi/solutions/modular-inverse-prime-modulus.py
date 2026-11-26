def main():
    import sys
    data = sys.stdin.read().strip()
    
    parts = data.split(',')
    a = int(parts[0].split('=')[1])
    m = int(parts[1].split('=')[1])
    
    def mod_pow(base, exp, mod):
        result = 1
        base = base % mod
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % mod
            exp = exp >> 1
            base = (base * base) % mod
        return result
    
    result = mod_pow(a, m - 2, m)
    print(result)

if __name__ == "__main__":
    main()
