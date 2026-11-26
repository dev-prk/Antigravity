import sys

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print("")
        return
    
    i = 0
    result = []
    
    while i < len(s):
        char = s[i]
        i += 1
        
        num_str = ""
        while i < len(s) and s[i].isdigit():
            num_str += s[i]
            i += 1
        
        if num_str:
            count = int(num_str)
            result.append(char * count)
        else:
            result.append(char)
    
    print("".join(result))

if __name__ == "__main__":
    main()
