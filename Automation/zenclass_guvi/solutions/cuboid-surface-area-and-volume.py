import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 3:
        return
    L = int(data[0])
    B = int(data[1])
    H = int(data[2])
    surface_area = 2 * (L * B + B * H + H * L)
    volume = L * B * H
    print(surface_area, volume)

if __name__ == "__main__":
    main()
