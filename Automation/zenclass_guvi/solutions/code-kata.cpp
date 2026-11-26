#include <iostream>
#include <string>
using namespace std;

// Virtual base class to resolve diamond problem
class Person {
protected:
    string name;
    int id;
public:
    Person(string n, int i) : name(n), id(i) {
        cout << "Person Constructor" << endl;
    }
    ~Person() {}
};

// Manager inherits virtually from Person
class Manager : virtual public Person {
protected:
    string department;
public:
    Manager(string n, int i, string d) : Person(n, i), department(d) {
        cout << "Manager Constructor" << endl;
    }
    ~Manager() {}
};

// Engineer inherits virtually from Person
class Engineer : virtual public Person {
protected:
    string project;
public:
    Engineer(string n, int i, string p) : Person(n, i), project(p) {
        cout << "Engineer Constructor" << endl;
    }
    ~Engineer() {}
};

// TechLead inherits from both Manager and Engineer
// Only one Person object exists due to virtual inheritance
class TechLead : public Manager, public Engineer {
public:
    TechLead(string name, int id, string dept, string proj) 
        : Person(name, id), Manager(name, id, dept), Engineer(name, id, proj) {
        cout << "TechLead Constructor" << endl;
    }
    
    void display() {
        cout << "Name: " << name << " ID: " << id 
             << " Dept: " << department << " Project: " << project << endl;
    }
};

int main() {
    string name, dept, proj;
    int id;
    
    getline(cin, name);
    cin >> id;
    cin.ignore();
    getline(cin, dept);
    getline(cin, proj);
    
    TechLead tl(name, id, dept, proj);
    tl.display();
    
    return 0;
}
