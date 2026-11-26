class Vehicle:
    def __init__(self, vehicleName, vehicleNumber):
        self.vehicleName = vehicleName
        self.vehicleNumber = vehicleNumber

class Car(Vehicle):
    def __init__(self, vehicleName, vehicleNumber, mileage):
        super().__init__(vehicleName, vehicleNumber)
        self.mileage = mileage

if __name__ == "__main__":
    vehicleName = input().strip()
    vehicleNumber = input().strip()
    mileage = int(input().strip())
    
    car = Car(vehicleName, vehicleNumber, mileage)
    
    print(f"Vehicle Name: {car.vehicleName}")
    print(f"Vehicle Number: {car.vehicleNumber}")
    print(f"Mileage: {car.mileage}")
    print(f"Distance for 10 Litres: {car.mileage * 10}")
