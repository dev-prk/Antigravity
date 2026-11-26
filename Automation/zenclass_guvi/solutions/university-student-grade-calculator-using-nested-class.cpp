#include <iostream>
#include <string>
using namespace std;

class University {
public:
    class Student {
    private:
        string name;
        int marks;
    public:
        Student(string n, int m) : name(n), marks(m) {}
        char computeGrade() {
            if (marks >= 80) return 'A';
            else if (marks >= 60) return 'B';
            else return 'C';
        }
    };
};

int main() {
    string name;
    int marks;
    if (cin >> name >> marks) {
        University::Student student(name, marks);
        cout << student.computeGrade() << endl;
    }
    return 0;
}
