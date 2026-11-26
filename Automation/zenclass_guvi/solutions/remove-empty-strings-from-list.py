import sys

def main():
    # Read the first line (size of list)
    n = int(sys.stdin.readline().strip())
    
    # Read the second line (list elements)
    line = sys.stdin.readline().strip()
    
    # Split by comma and filter out empty strings
    if line == '':
        result = []
    else:
        elements = line.split(',')
        result = [elem.strip() for elem in elements if elem.strip() != '']
    
    # Output the result joined by comma
    print(','.join(result))

if __name__ == "__main__":
    main()
