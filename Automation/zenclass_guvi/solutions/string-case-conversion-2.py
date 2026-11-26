import sys

def main():
    # Read all input lines and strip whitespace
    lines = [line.strip() for line in sys.stdin.readlines()]
    
    if len(lines) < 3:
        return
    
    S = lines[0]
    try:
        T = int(lines[1])
        P = int(lines[2])
    except ValueError:
        return
    
    # Handle edge cases
    if P <= 0 or len(S) == 0:
        print(S)
        return
    
    result = []
    
    for i in range(len(S)):
        pos = i + 1  # 1-based indexing
        
        if pos % P == 0 and S[i].isalpha():
            if T == 1:  # Convert to lowercase
                result.append(S[i].lower())
            elif T == 2:  # Convert to uppercase
                result.append(S[i].upper())
            else:
                result.append(S[i])
        else:
            result.append(S[i])
    
    print(''.join(result))

if __name__ == "__main__":
    main()
