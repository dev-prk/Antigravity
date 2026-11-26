import sys

def main():
    data = sys.stdin.read()
    # Remove only trailing newline characters, preserve other whitespace
    while data.endswith('\n') or data.endswith('\r'):
        data = data[:-1]
    vowels = set('aeiouAEIOU')
    result = ''.join(ch for ch in data if ch not in vowels)
    sys.stdout.write(result)

if __name__ == "__main__":
    main()
