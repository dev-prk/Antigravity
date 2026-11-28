import sys
import math

def main():
    data = sys.stdin.read().strip()
    if not data:
        print("Error")
        return
    
    try:
        r = float(data)
    except ValueError:
        print("Error")
        return
    
    if r < 0:
        print("Error")
        return
    
    circumference = 2 * math.pi * r
    print(f"{circumference:.2f}")

if __name__ == "__main__":
    main()
