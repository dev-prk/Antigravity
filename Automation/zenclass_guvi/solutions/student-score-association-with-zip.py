import sys
import ast

def associate_students(names, scores):
    return list(zip(names, scores))

def main():
    # Read the entire input
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        return
    
    # Parse the input as a Python literal (list of names)
    # Input format: ['Alice', 'Bob', 'Charlie', 'Dave'], [85, 90, 78, 92]
    # Find the comma that separates the two lists
    comma_idx = input_data.find('], [')
    
    if comma_idx == -1:
        return
    
    # Extract the two lists
    names_str = input_data[:comma_idx + 1]
    scores_str = input_data[comma_idx + 3:]
    
    # Parse the lists
    names = ast.literal_eval(names_str)
    scores = ast.literal_eval(scores_str)
    
    # Call the function and print the result
    result = associate_students(names, scores)
    print(repr(result))

if __name__ == "__main__":
    main()
