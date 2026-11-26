import sys

def caesar_cipher(s, shift):
    result = []
    for char in s:
        if char.isupper():
            result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
        elif char.islower():
            result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
        else:
            result.append(char)
    return ''.join(result)

def main():
    line = sys.stdin.readline().rstrip('\n')
    if not line:
        return
    parts = line.rsplit(' ', 1)
    if len(parts) != 2:
        return
    s = parts[0].rstrip(' ')
    try:
        shift = int(parts[1])
    except ValueError:
        return
    print(caesar_cipher(s, shift))

if __name__ == "__main__":
    main()
