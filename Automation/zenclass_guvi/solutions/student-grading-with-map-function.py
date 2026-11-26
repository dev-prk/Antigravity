def get_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def grade_students(scores):
    return list(map(get_grade, scores))

# Read input from sys.stdin and execute
import sys

def main():
    # Read the entire input
    input_data = sys.stdin.read().strip()
    
    # Handle empty input
    if not input_data:
        print([])
        return
    
    # Parse the input as a Python list literal
    # Remove brackets and parse numbers
    input_data = input_data.strip()
    if input_data.startswith('['):
        input_data = input_data[1:]
    if input_data.endswith(']'):
        input_data = input_data[:-1]
    
    # Split by comma and clean up
    if not input_data.strip():
        print([])
        return
    
    scores = []
    for item in input_data.split(','):
        item = item.strip()
        if item:
            scores.append(int(item))
    
    # Get grades and print
    result = grade_students(scores)
    # Format output with space after comma (matching expected output format)
    output = '[' + ', '.join("'" + grade + "'" for grade in result) + ']'
    print(output)

if __name__ == "__main__":
    main()
