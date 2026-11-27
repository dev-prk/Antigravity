import sys
from collections import deque, Counter

def main():
    stream = sys.stdin.readline().strip()
    freq = Counter()
    q = deque()
    
    for ch in stream:
        freq[ch] += 1
        if freq[ch] == 1:
            q.append(ch)
        elif freq[ch] == 2:
            while q and freq[q[0]] > 1:
                q.popleft()
        
        if q:
            print(q[0], end=' ')
        else:
            print(-1, end=' ')

if __name__ == "__main__":
    main()
