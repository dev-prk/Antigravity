import sys

def main():
    n = int(sys.stdin.readline().strip())
    arr = []
    for _ in range(n):
        word = sys.stdin.readline().strip()
        if word == "null":
            arr.append(None)
        else:
            arr.append(word)
    
    for item in arr:
        try:
            print(len(item))
        except TypeError:
            print("Error: Null reference encountered")

if __name__ == "__main__":
    main()
