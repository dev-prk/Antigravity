import sys

def main():
    data = sys.stdin.read().split()
    marks = [int(x) for x in data[:5]]

    if not marks:
        print("Total Marks: 0")
        print("Average Marks: 0")
        print("Highest Mark: 0")
        print("Lowest Mark: 0")
        return

    total = sum(marks)
    average = total // 5
    highest = max(marks)
    lowest = min(marks)

    print(f"Total Marks: {total}")
    print(f"Average Marks: {average}")
    print(f"Highest Mark: {highest}")
    print(f"Lowest Mark: {lowest}")

if __name__ == "__main__":
    main()
