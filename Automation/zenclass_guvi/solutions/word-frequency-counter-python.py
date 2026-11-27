from collections import Counter
import sys

def main():
    # Read the sentence from stdin
    sentence = sys.stdin.readline().strip()
    
    # Handle empty input
    if not sentence:
        return
    
    # Split the sentence into words
    words = sentence.split()
    
    # Count word frequencies
    word_count = Counter(words)
    
    # Sort words alphabetically and print
    for word in sorted(word_count.keys()):
        print(f"{word} {word_count[word]}")

if __name__ == "__main__":
    main()
