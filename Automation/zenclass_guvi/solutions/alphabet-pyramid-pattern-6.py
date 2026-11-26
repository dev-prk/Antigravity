import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    # Take the first integer found
    try:
        R = int(data.split()[0])
    except:
        return
    
    out_lines = []
    for i in range(1, R + 1):
        leading_spaces = ' ' * (R - i)
        letters = ' '.join(chr(ord('A') + j) for j in range(i))
        out_lines.append(leading_spaces + letters)
    
    sys.stdout.write('\n'.join(out_lines))

if __name__ == "__main__":
    main()
