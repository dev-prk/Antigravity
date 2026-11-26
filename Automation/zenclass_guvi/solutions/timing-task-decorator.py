import sys
import time
from functools import wraps

def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed = round(end - start, 2)
        print(f"{args[0][0]} took {elapsed} seconds")
        return result
    return wrapper

@time_it
def do_task(task):
    time.sleep(task[1])

if __name__ == "__main__":
    line = sys.stdin.readline().strip()
    if line:
        parts = line.split(", ")
        task_name = parts[0].strip()
        task_duration = int(parts[1].strip()) if len(parts) > 1 else int(line.split()[-1])
        task = (task_name, task_duration)
        do_task(task)
