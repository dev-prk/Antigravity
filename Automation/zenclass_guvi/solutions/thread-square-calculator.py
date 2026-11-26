from threading import Thread
import sys

class SquareThread(Thread):
    def __init__(self, num):
        Thread.__init__(self)
        self.num = num
        self.result = None
    
    def run(self):
        self.result = self.num * self.num

def main():
    line = sys.stdin.readline()
    if line.strip() == '':
        print("Square: 0")
        return
    num = int(line.strip())
    t = SquareThread(num)
    t.start()
    t.join()
    print("Square: " + str(t.result))

if __name__ == "__main__":
    main()
