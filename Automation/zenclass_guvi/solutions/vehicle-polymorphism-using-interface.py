import sys
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def getSpeed(self):
        pass

    @abstractmethod
    def display(self):
        pass

class Car(Vehicle):
    def __init__(self, speed):
        self.speed = speed
    def getSpeed(self):
        return self.speed
    def display(self):
        print(f"Car Speed: {self.getSpeed()}")

class Bike(Vehicle):
    def __init__(self, speed):
        self.speed = speed
    def getSpeed(self):
        return self.speed
    def display(self):
        print(f"Bike Speed: {self.getSpeed()}")

class Bus(Vehicle):
    def __init__(self, speed):
        self.speed = speed
    def getSpeed(self):
        return self.speed
    def display(self):
        print(f"Bus Speed: {self.getSpeed()}")

def main():
    lines = sys.stdin.read().strip().splitlines()
    if not lines:
        return
    vtype = lines[0].strip().lower()
    speed = int(lines[1].strip())
    if vtype == "car":
        v = Car(speed)
    elif vtype == "bike":
        v = Bike(speed)
    elif vtype == "bus":
        v = Bus(speed)
    else:
        return
    v.display()

if __name__ == "__main__":
    main()
