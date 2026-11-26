from functools import reduce
import sys

def total_score(scores):
    return reduce(lambda x, y: x + y, scores, 0)

# Read input from sys.stdin and execute
if __name__ == "__main__":
    # Read the entire input
    input_data = sys.stdin.read().strip()
    
    # If input is empty, return 0
    if not input_data:
        print(0)
    else:
        # Parse the input as a list of integers
        # Input format: [85, 90, 78, 92]
        scores = eval(input_data)
        result = total_score(scores)
        print(result)
