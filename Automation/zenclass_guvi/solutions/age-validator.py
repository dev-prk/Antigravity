def main():
    try:
        age = int(input().strip())
        if age < 0:
            raise ValueError("Invalid age")
        print(f"Valid age: {age}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
