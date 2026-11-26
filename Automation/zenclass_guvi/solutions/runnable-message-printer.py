import sys
import threading

class MessagePrinter(threading.Thread):
    def __init__(self, message, count):
        super().__init__()
        self.message = message
        self.count = count
    
    def run(self):
        for _ in range(self.count):
            print(self.message)

def main():
    message = sys.stdin.readline().strip()
    count = int(sys.stdin.readline().strip())
    
    printer = MessagePrinter(message, count)
    printer.start()
    printer.join()
    
    print("Finished")

if __name__ == "__main__":
    main()
