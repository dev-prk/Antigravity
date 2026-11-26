import sys
import bisect

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    existing = []
    for _ in range(n):
        existing.append(int(data[idx]))
        idx += 1
    
    m = int(data[idx])
    idx += 1
    
    new_books = []
    for _ in range(m):
        new_books.append(int(data[idx]))
        idx += 1
    
    neg_existing = [-x for x in existing]
    
    result = []
    for book in new_books:
        neg_book = -book
        pos = bisect.bisect_right(neg_existing, neg_book)
        result.append(str(pos + 1))
    
    print(' '.join(result))

if __name__ == "__main__":
    main()
