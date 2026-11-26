import sys

def camel_case_conversion(s):
    words = s.split()
    if not words:
        return ""
    result = [words[0].lower()]
    for word in words[1:]:
        if word:
            result.append(word[0].upper() + word[1:].lower())
    return ''.join(result)

def main():
    s = sys.stdin.read().strip()
    if not s:
        print("")
        return
    print(camel_case_conversion(s))

if __name__ == "__main__":
    main()
