# Problem: 1095 - Iterating Student Data
# Iterative Student Data Management System

def iterate_students(students):
    """
    Iterates over a list of student dictionaries and prints each student's details.
    
    Args:
        students: List of dictionaries containing student data with keys:
                  'id', 'name', 'course', 'grade'
    """
    for student in students:
        print(f"Student ID: {student['id']}, Name: {student['name']}, Course: {student['course']}, Grade: {student['grade']}")

# Main execution - reads from stdin and writes to stdout
if __name__ == "__main__":
    import ast
    import sys
    
    # Read the entire input
    input_data = sys.stdin.read().strip()
    
    # Handle empty input
    if not input_data:
        sys.exit(0)
    
    # Parse the input as a Python literal (list of dictionaries)
    students = ast.literal_eval(input_data)
    
    # Iterate and print each student's details
    iterate_students(students)
