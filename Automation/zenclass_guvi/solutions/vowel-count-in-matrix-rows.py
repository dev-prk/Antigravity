import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 25:
        print(0)
        return
    # Build 5x5 matrix from the first 25 tokens
    matrix = [data[i*5:(i+1)*5] for i in range(5)]
    vowels = set('aeiou')
    count = 0
    for row in matrix:
        found = set()
        for ch in row:
            found.add(ch.lower())
        # check if all 5 distinct vowels are present
        if found >= vowels:
            count += 1
    print(count)

if __name__ == "__main__":
    main()
