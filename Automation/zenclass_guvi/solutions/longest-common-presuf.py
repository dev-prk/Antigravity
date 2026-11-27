def main():
    import sys
    input = sys.stdin.read().splitlines()
    if not input:
        print("No common prefux exists")
        return
    
    first_line = input[0].split()
    n = int(first_line[0])
    
    if n == 0:
        print("No common presuf exists")
        return
    
    strings = input[1:1+n]
    
    odd_strings = []  # 1st, 3rd, 5th... (indices 0, 2, 4...)
    even_strings = []  # 2nd, 4th, 6th... (indices 1, 3, 5...)
    
    for i in range(n):
        if i % 2 == 0:  # odd index (1st, 3rd, etc.)
            odd_strings.append(strings[i])
        else:  # even index (2nd, 4th, etc.)
            even_strings.append(strings[i][::-1])  # reverse the string
    
    # Find common prefix of odd strings
    if not odd_strings:
        prefix = ""
    else:
        prefix = odd_strings[0]
        for s in odd_strings[1:]:
            min_len = min(len(prefix), len(s))
            i = 0
            while i < min_len and prefix[i] == s[i]:
                i += 1
            prefix = prefix[:i]
    
    # Find common prefix of reversed even strings (which is common suffix of original even strings)
    if not even_strings:
        suffix = ""
    else:
        suffix = even_strings[0]
        for s in even_strings[1:]:
            min_len = min(len(suffix), len(s))
            i = 0
            while i < min_len and suffix[i] == s[i]:
                i += 1
            suffix = suffix[:i]
    
    # Find the longest common presuf
    # It must be both a prefix of odd strings AND a reversed suffix of even strings
    result = ""
    min_len = min(len(prefix), len(suffix))
    for i in range(min_len + 1):
        if prefix[:i] == suffix[:i]:
            result = prefix[:i]
    
    if result:
        print(result)
    else:
        print("No common presuf exists")

if __name__ == "__main__":
    main()
