import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return

    negative = False
    if data[0] in '+-':
        negative = data[0] == '-'
        data = data[1:]

    if not data:
        value = 0
    else:
        value = int(data, 2)

    result = format(value, 'X')
    if negative and value != 0:
        result = '-' + result

    print(result)

if __name__ == '__main__':
    main()
