import sys

def main():
    lines = sys.stdin.read().strip().split()
    if len(lines) < 2:
        return
    
    id_card = int(lines[0])
    helmet = int(lines[1])
    
    if id_card == 0:
        print("Show ID Card")
    elif helmet == 0:
        print("Wear Helmet")
    else:
        print("Entry Allowed")

if __name__ == "__main__":
    main()
