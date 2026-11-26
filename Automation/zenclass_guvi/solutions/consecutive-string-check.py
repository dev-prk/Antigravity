import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print('no')
        return
    
    n = int(data[0].strip())
    
    if n <= 1:
        print('no')
        return
    
    strings = []
    for i in range(1, n + 1):
        if i < len(data):
            strings.append(data[i].strip())
        else:
            strings.append('')
    
    for i in range(len(strings) - 1):
        if strings[i] == strings[i + 1]:
            print('yes')
            return
    
    print('no')

if __name__ == "__main__":
    main()
