import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    # Next n tokens are years
    years = []
    for i in range(n):
        years.append(int(data[1 + i]))
    start_idx = 1 + n
    parties = []
    for i in range(n):
        parties.append(data[start_idx + i])
    
    # Sort pairs by year
    pairs = sorted(zip(years, parties))
    
    result = []
    for i in range(len(pairs) - 1):
        if pairs[i][1] != pairs[i + 1][1]:
            result.append(str(pairs[i + 1][0]))
    
    print('\n'.join(result))

main()
