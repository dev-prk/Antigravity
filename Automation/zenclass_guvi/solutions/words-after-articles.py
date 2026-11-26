import sys

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print(-1)
        return
    
    words = s.split()
    articles = {'a', 'an', 'the'}
    result = []
    
    for i in range(len(words) - 1):
        if words[i].lower() in articles:
            result.append(words[i + 1])
    
    if not result:
        print(-1)
    else:
        print(' '.join(result))

if __name__ == "__main__":
    main()
