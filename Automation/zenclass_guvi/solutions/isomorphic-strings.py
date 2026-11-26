import sys

def main():
    line = sys.stdin.readline().strip()
    if not line:
        print('no')
        return
    
    parts = line.split()
    if len(parts) < 2:
        print('no')
        return
    
    s = parts[0]
    t = parts[1]
    
    if len(s) != len(t):
        print('no')
        return
    
    if len(s) == 0:
        print('yes')
        return
    
    map_s_to_t = {}
    map_t_to_s = {}
    
    for i in range(len(s)):
        char_s = s[i]
        char_t = t[i]
        
        if char_s in map_s_to_t:
            if map_s_to_t[char_s] != char_t:
                print('no')
                return
        else:
            map_s_to_t[char_s] = char_t
        
        if char_t in map_t_to_s:
            if map_t_to_s[char_t] != char_s:
                print('no')
                return
        else:
            map_t_to_s[char_t] = char_s
    
    print('yes')

if __name__ == "__main__":
    main()
