import sys

def main():
    lines = sys.stdin.read().strip().split()
    weight = int(lines[0])
    damaged_seals = int(lines[1])
    shelf_life = int(lines[2])
    
    is_good_weight = 495 <= weight <= 505
    no_damaged_seals = damaged_seals == 0
    good_shelf_life = shelf_life >= 30
    
    result = is_good_weight and no_damaged_seals and good_shelf_life
    print(result)

if __name__ == "__main__":
    main()
