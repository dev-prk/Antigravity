import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(0)
        return
    
    n_barriers = int(data[0])
    n_tracks = int(data[1])
    
    barriers = []
    idx = 2
    for i in range(n_barriers):
        start = int(data[idx])
        end = int(data[idx + 1])
        barriers.append((start, end))
        idx += 2
    
    if n_barriers == 0:
        print(n_tracks)
        return
    
    barriers.sort(key=lambda x: x[0])
    
    merged = []
    for barrier in barriers:
        if not merged:
            merged.append(list(barrier))
        else:
            last = merged[-1]
            if barrier[0] <= last[1] + 1:
                last[1] = max(last[1], barrier[1])
            else:
                merged.append(list(barrier))
    
    blocked_tracks = 0
    for start, end in merged:
        blocked_tracks += (end - start + 1)
    
    result = n_tracks - blocked_tracks
    print(result)

if __name__ == "__main__":
    main()
