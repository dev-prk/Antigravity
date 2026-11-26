class Vehicle:
    def __init__(self, vehicleNumber, brand):
        self.vehicleNumber = vehicleNumber
        self.brand = brand

class Car(Vehicle):
    def __init__(self, vehicleNumber, brand, seatingCapacity):
        super().__init__(vehicleNumber, brand)
        self.seatingCapacity = seatingCapacity

class ElectricCar(Car):
    def __init__(self, vehicleNumber, brand, seatingCapacity, batteryCapacity):
        super().__init__(vehicleNumber, brand, seatingCapacity)
        self.batteryCapacity = batteryCapacity

    def displayInfo(self):
        print(f"Vehicle Number: {self.vehicleNumber}")
        print(f"Brand: {self.brand}")
        print(f"Seating Capacity: {self.seatingCapacity}")
        print(f"Battery Capacity: {self.batteryCapacity}")

if __name__ == "__main__":
    vehicleNumber = input().strip()
    brand = input().strip()
    seatingCapacity = input().strip()
    batteryCapacity = input().strip()
    car = ElectricCar(vehicleNumber, brand, seatingCapacity, batteryCapacity)
    car.displayInfo()
