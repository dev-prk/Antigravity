import sys

def main():
    weapons = []
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.rsplit(' ', 1)
        if len(parts) == 2:
            name, power_str = parts
            try:
                power = int(power_str)
                weapons.append((power, name))
            except ValueError:
                continue
    
    # Sort by power (first element of tuple)
    weapons.sort(key=lambda x: x[0])
    
    # Output with ranking
    for i, (power, name) in enumerate(weapons, 1):
        print(f"{i} {name}")

if __name__ == "__main__":
    main()
