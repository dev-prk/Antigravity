#include <iostream>
#include <fstream>
#include <cstring>
using namespace std;

class Employee {
public:
    int id;
    char name[20];
    double salary;

    void input() {
        cin >> id;
        cin >> name;
        cin >> salary;
    }

    void display() {
        cout << "ID: " << id << endl;
        cout << "Name: " << name << endl;
        cout << "Salary: " << salary << endl;
    }
};

int main() {
    int n;
    cin >> n;

    ofstream outfile("employees.dat", ios::binary);
    for (int i = 0; i < n; i++) {
        Employee emp;
        emp.input();
        outfile.write(reinterpret_cast<char*>(&emp), sizeof(Employee));
    }
    outfile.close();

    int r;
    cin >> r;

    ifstream infile("employees.dat", ios::binary);
    Employee emp;
    infile.seekg((r - 1) * sizeof(Employee));
    if (infile.read(reinterpret_cast<char*>(&emp), sizeof(Employee))) {
        cout << "Employee Found:" << endl;
        emp.display();
    } else {
        cout << "Record not found" << endl;
    }
    infile.close();

    return 0;
}
