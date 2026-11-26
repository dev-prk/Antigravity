import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print("No common prefix exists")
        return
    
    n = int(data[0])
    if n == 0:
        print("No common prefix exists")
        return
    
    strings = data[1:n+1]
    if not strings:
        print("No common prefix exists")
        return
    
    # Find minimum length string
    min_len = min(len(s) for s in strings)
    
    if min_len == 0:
        print("No common prefix exists")
        return
    
    # Compare character by character
    prefix_len = 0
    for i in range(min_len):
        char = strings[0][i]
        if all(s[i] == char for s in strings):
            prefix_len += 1
        else:
            break
    
    if prefix_len == 0:
        print("No common prefix exists")
    else:
        print(strings[0][:prefix_len])

if __name__ == "__main__":
    main()
