import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data)
    
    if n > 0:
        num_type = "Positive"
    elif n < 0:
        num_type = "Negative"
    else:
        num_type = "Zero"
    
    parity = "Even" if n % 2 == 0 else "Odd"
    square = n * n
    cube = n * n * n
    
    print(f"Number Type: {num_type}")
    print(f"Parity: {parity}")
    print(f"Square: {square}")
    print(f"Cube: {cube}")

if __name__ == "__main__":
    main()
