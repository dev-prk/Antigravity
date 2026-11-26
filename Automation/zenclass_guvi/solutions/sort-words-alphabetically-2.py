import sys

def main():
    # Read the entire input and strip any leading/trailing whitespace
    input_string = sys.stdin.read().strip()
    
    # Handle empty input case
    if not input_string:
        print(-1)
        return
    
    # Split the string into words
    words = input_string.split()
    
    # Handle case where there are no words after splitting
    if not words:
        print(-1)
        return
    
    # Sort the words alphabetically
    sorted_words = sorted(words)
    
    # Join the sorted words with a single space and print
    print(' '.join(sorted_words))

if __name__ == "__main__":
    main()
