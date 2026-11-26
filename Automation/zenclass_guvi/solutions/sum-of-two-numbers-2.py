def main():
    try:
        line1 = input().strip()
        line2 = input().strip()
        
        if line1 == '' or line2 == '':
            print(0)
            return
        
        a = float(line1)
        b = float(line2)
        
        c = a + b
        
        if c == int(c):
            print(int(c))
        else:
            print(round(c, 1))
    except EOFError:
        print(0)
    except ValueError:
        print(0)

if __name__ == "__main__":
    main()
