import sys

def main():
    good_parts = 0
    heavy_parts = 0
    good_weight_total = 0
    
    for line in sys.stdin:
        weight = int(line.strip())
        if weight == 0:
            break
        if weight < 10:
            continue
        elif weight > 100:
            heavy_parts += 1
        else:
            good_parts += 1
            good_weight_total += weight
    
    print(good_parts)
    print(heavy_parts)
    print(good_weight_total)

if __name__ == "__main__":
    main()
