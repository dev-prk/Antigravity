import sys
import threading

class Counter(threading.Thread):
    def __init__(self, n):
        super().__init__()
        self.n = n
    def run(self):
        for i in range(1, self.n + 1):
            print(i)

def main():
    data = sys.stdin.read().strip()
    if data:
        n = int(data)
        t = Counter(n)
        t.start()
        t.join()
        print("Done")

if __name__ == "__main__":
    main()
