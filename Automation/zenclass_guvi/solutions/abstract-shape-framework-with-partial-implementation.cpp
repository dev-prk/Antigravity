#include <iostream>
#include <iomanip>
using namespace std;

class Shape {
public:
    virtual double area() = 0;
    virtual void describe() { cout << "Shape Description" << endl; }
    virtual ~Shape() {}
};

class Triangle : public Shape {
private:
    double base, height;
public:
    Triangle(double b, double h) : base(b), height(h) {}
    double area() override { return 0.5 * base * height; }
    void describe() override {
        cout << "Shape Description" << endl;
        cout << "Triangle Area: " << fixed << setprecision(2) << area() << endl;
    }
    ~Triangle() {}
};

class Square : public Shape {
private:
    double side;
public:
    Square(double s) : side(s) {}
    double area() override { return side * side; }
    void describe() override {
        cout << "Shape Description" << endl;
        cout << "Square Area: " << fixed << setprecision(2) << area() << endl;
    }
    ~Square() {}
};

int main() {
    double base, height, side;
    cin >> base >> height >> side;
    
    Shape* shapes[2];
    shapes[0] = new Triangle(base, height);
    shapes[1] = new Square(side);
    
    for (int i = 0; i < 2; i++) {
        shapes[i]->describe();
    }
    
    for (int i = 0; i < 2; i++) {
        delete shapes[i];
    }
    
    return 0;
}
