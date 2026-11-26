import sys
import time

class MarriageFunction:
    total_duration = 0.0

    @classmethod
    def do_task(cls, task):
        start = time.time()
        time.sleep(1)
        end = time.time()
        elapsed = end - start
        cls.total_duration += elapsed
        print(f"{task[0]} took {task[1]}.0 seconds")

if __name__ == "__main__":
    tasks = eval(sys.stdin.read())
    for task in tasks:
        MarriageFunction.do_task(task)
