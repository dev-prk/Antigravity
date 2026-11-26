import sys


class Triangle:
    def __init__(self):
        self.a = 0
        self.b = 0
        self.c = 0

    def set_sides(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def perimeter(self):
        return self.a + self.b + self.c


def main():
    data = sys.stdin.read().split()
    nums = [int(x) for x in data[:3]]
    while len(nums) < 3:
        nums.append(0)
    t = Triangle()
    t.set_sides(nums[0], nums[1], nums[2])
    print(t.perimeter())


if __name__ == "__main__":
    main()
