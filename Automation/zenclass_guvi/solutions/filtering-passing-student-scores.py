import sys, ast

def passed_students(scores):
    return list(filter(lambda s: s >= 60, scores))

if __name__ == "__main__":
    data = sys.stdin.read().strip()
    if data:
        scores = ast.literal_eval(data)
        result = passed_students(scores)
        print(result)
