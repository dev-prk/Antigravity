import sys

def main():
    data = sys.stdin.read().split()
    if not data:
        print(-1)
        return
    n = int(data[0])
    petrol = []
    distance = []
    idx = 1
    for i in range(n):
        p = int(data[idx])
        d = int(data[idx + 1])
        idx += 2
        petrol.append(p)
        distance.append(d)

    if n == 0:
        print(-1)
        return

    total_petrol = sum(petrol)
    total_distance = sum(distance)

    if total_petrol < total_distance:
        print(-1)
        return

    tank = 0
    start = 0
    for i in range(n):
        tank += petrol[i] - distance[i]
        if tank < 0:
            tank = 0
            start = i + 1

    print(start)

if __name__ == "__main__":
    main()
