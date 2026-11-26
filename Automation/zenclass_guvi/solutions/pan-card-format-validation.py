import sys

def is_pan_card(s):
    s = s.strip()
    if len(s) != 10:
        return False
    if not s[:5].isalpha():
        return False
    if not s[5:9].isdigit():
        return False
    if not s[9].isalpha():
        return False
    return True

def main():
    s = sys.stdin.readline()
    if is_pan_card(s):
        print("Yes")
    else:
        print("No")

if __name__ == "__main__":
    main()
