import sys

def main():
    s = sys.stdin.read()
    vowels = set("aeiouAEIOU")
    print(sum(1 for ch in s if ch in vowels))

if __name__ == "__main__":
    main()
