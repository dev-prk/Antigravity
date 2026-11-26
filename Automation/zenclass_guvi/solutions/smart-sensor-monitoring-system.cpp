#include <iostream>
#include <iomanip>
using namespace std;

class Sensor {
private:
    int sensorID;
    double temperature;
    static int totalSensors;

public:
    Sensor(int id, double temp) : sensorID(id), temperature(temp) {
        totalSensors++;
    }

    void updateTemperature(double temp) volatile {
        temperature = temp;
    }

    double getTemperature() const volatile {
        return temperature;
    }

    static int getTotalSensors() {
        return totalSensors;
    }
};

int Sensor::totalSensors = 0;

int main() {
    int id;
    double temp, newTemp;
    
    cin >> id >> temp;
    cin >> newTemp;
    
    volatile Sensor s(id, temp);
    
    cout << fixed << setprecision(2);
    cout << "Initial Temperature: " << s.getTemperature() << endl;
    
    s.updateTemperature(newTemp);
    
    cout << "Updated Temperature: " << s.getTemperature() << endl;
    cout << "Total Sensors Created: " << Sensor::getTotalSensors() << endl;
    
    return 0;
}
