import sys

# Define the custom exception
class StudentNotFoundError(Exception):
    def __init__(self, message="Student not found"):
        self.message = message
        super().__init__(self.message)

# Define the student database
students = {
    "BT202101": "A",
    "BT202102": "B"
}

# Original function
def get_student_grade(student_id: str) -> str:
    if student_id not in students:
        raise StudentNotFoundError("Student not found")
    return students[student_id]

# Proxy function with error handling
def proxy_get_student_grade(student_id: str) -> str:
    try:
        return get_student_grade(student_id)
    except StudentNotFoundError:
        return 'N/A'

# Read input and print output
if __name__ == "__main__":
    student_id = sys.stdin.readline().strip()
    result = proxy_get_student_grade(student_id)
    print(result)
