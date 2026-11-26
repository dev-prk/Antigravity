class Calculator:
    def add(self, a, b):
        return a + b
    
    def add_three(self, a, b, c):
        return a + b + c
    
    def add_doubles(self, a, b):
        return a + b

def main():
    import sys
    
    lines = []
    for line in sys.stdin:
        lines.append(line.strip())
    
    nums = [int(x) if '.' not in x else float(x) for x in lines]
    
    a = int(nums[0])
    b = int(nums[1])
    c = int(nums[2])
    d = nums[3]
    e = nums[4]
    
    calc = Calculator()
    
    two_int = calc.add(a, b)
    three_int = calc.add_three(a, b, c)
    two_double = calc.add_doubles(d, e)
    
    print(f"Addition of Two Integers: {two_int}")
    print(f"Addition of Three Integers: {three_int}")
    print(f"Addition of Two Doubles: {two_double}")

if __name__ == "__main__":
    main()
