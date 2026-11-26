import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    n = int(data[0].strip())
    dictionary = set()
    
    for i in range(1, n + 1):
        word = data[i].strip()
        if word in dictionary:
            print("Word found")
        else:
            print("Word not found , added to dictionary")
            dictionary.add(word)

if __name__ == "__main__":
    main()
