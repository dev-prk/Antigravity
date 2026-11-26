import sys
from collections import Counter

def main():
    data = sys.stdin.read()
    if not data:
        return
    text = data.strip()
    if not text:
        print()
        return

    # Count frequencies of alphabetic characters (case-insensitive)
    freq = Counter(ch.lower() for ch in text if ch.isalpha())

    words = text.split()
    result = []
    for word in words:
        new_word = []
        for ch in word:
            if ch.isalpha() and freq[ch.lower()] > 1:
                new_word.append(ch.upper())
            else:
                new_word.append(ch.lower())
        result.append(''.join(new_word))

    sys.stdout.write(' '.join(result))

if __name__ == "__main__":
    main()
