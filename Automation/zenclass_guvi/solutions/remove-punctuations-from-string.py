import sys, string

def main():
    data = sys.stdin.read()
    table = str.maketrans('', '', string.punctuation)
    result = data.translate(table)
    sys.stdout.write(result)

if __name__ == '__main__':
    main()
