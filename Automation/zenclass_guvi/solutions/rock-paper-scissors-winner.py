import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    a, b = data[0], data[1]
    if a == b:
        print('D')
        return
    beats = {'R': 'S', 'S': 'P', 'P': 'R'}
    print(a if beats[a] == b else b)

if __name__ == '__main__':
    main()
