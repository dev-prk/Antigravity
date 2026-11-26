#include <iostream>
#include <string>
using namespace std;

class Car {
private:
    string make;
    string model;
    int year;

public:
    Car(string m, string mod, int y) : make(m), model(mod), year(y) {}

    int getCarAge(int currentYear) {
        return currentYear - year;
    }

    bool isValidYear(int currentYear) {
        return year <= currentYear;
    }
};

int main() {
    string make, model;
    int year, currentYear;

    // Read lines instead of using >> operator
    getline(cin, make);
    getline(cin, model);
    cin >> year >> currentYear;

    Car car(make, model, year);

    if (!car.isValidYear(currentYear)) {
        cout << "Invalid year" << endl;
    } else {
        cout << car.getCarAge(currentYear) << endl;
    }

    return 0;
}
