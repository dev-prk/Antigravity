import sys

class ElectronicDevice:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Mobile(ElectronicDevice):
    def __init__(self, name, price, screen_size):
        super().__init__(name, price)
        self.screen_size = screen_size
    
    def print_details(self):
        print(f"Mobile: {self.name}, Price: ${self.price}, Screen Size: {self.screen_size}")

class Laptop(ElectronicDevice):
    def __init__(self, name, price, screen_resolution):
        super().__init__(name, price)
        self.screen_resolution = screen_resolution
    
    def print_details(self):
        print(f"Laptop: {self.name}, Price: ${self.price}, Screen Resolution: {self.screen_resolution}")

def main():
    lines = sys.stdin.read().strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        parts = line.split(', ')
        name = parts[0].strip()
        price = parts[1].strip()
        third = parts[2].strip()
        
        if 'x' in third:
            device = Laptop(name, price, third)
        else:
            device = Mobile(name, price, third)
        
        device.print_details()

if __name__ == "__main__":
    main()
