import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    
    if '=' in data:
        n = int(data.split('=')[1].strip())
    else:
        n = int(data)
    
    if n < 2:
        print("[]")
        return
    
    spf = list(range(n + 1))
    primes = []
    
    for i in range(2, n + 1):
        if spf[i] == i:
            primes.append(i)
        for p in primes:
            if p > spf[i] or i * p > n:
                break
            spf[i * p] = p
    
    print("[" + ",".join(map(str, primes)) + "]")

if __name__ == "__main__":
    main()
