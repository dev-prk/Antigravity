#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <iomanip>

class ParkingLot {
private:
    int totalSlots;
    int availableSlots;
    int parkedVehicles;
    double ratePerHour;
    double totalRevenue;

public:
    void initialize(int slots, double rate) {
        totalSlots = slots;
        availableSlots = slots;
        parkedVehicles = 0;
        ratePerHour = rate;
        totalRevenue = 0.0;
    }

    bool parkVehicle() {
        if (availableSlots > 0) {
            availableSlots--;
            parkedVehicles++;
            return true;
        }
        return false;
    }

    bool removeVehicle(int hours) {
        if (parkedVehicles > 0) {
            double bill = hours * ratePerHour;
            totalRevenue += bill;
            availableSlots++;
            parkedVehicles--;
            std::cout << "Bill: " << std::fixed << std::setprecision(2) << bill << std::endl;
            return true;
        }
        return false;
    }

    void displayStatus() {
        std::cout << "Total Slots: " << totalSlots << std::endl;
        std::cout << "Available Slots: " << availableSlots << std::endl;
        std::cout << "Parked Vehicles: " << parkedVehicles << std::endl;
        std::cout << "Total Revenue: " << std::fixed << std::setprecision(2) << totalRevenue << std::endl;
    }
};

int main() {
    ParkingLot lot;
    
    int totalSlots, ratePerHourInt;
    std::cin >> totalSlots >> ratePerHourInt;
    lot.initialize(totalSlots, ratePerHourInt);
    
    int numberOfOperations;
    std::cin >> numberOfOperations;
    
    std::cin.ignore(); // Ignore newline after reading numberOfOperations
    
    for (int i = 0; i < numberOfOperations; i++) {
        std::string operation;
        std::getline(std::cin, operation);
        
        if (operation == "P") {
            if (!lot.parkVehicle()) {
                std::cout << "Parking Full" << std::endl;
            }
        }
        else if (operation[0] == 'R') {
            int hours = std::stoi(operation.substr(2));
            if (!lot.removeVehicle(hours)) {
                std::cout << "No Vehicles Parked" << std::endl;
            }
        }
        else if (operation == "S") {
            lot.displayStatus();
        }
    }
    
    return 0;
}
