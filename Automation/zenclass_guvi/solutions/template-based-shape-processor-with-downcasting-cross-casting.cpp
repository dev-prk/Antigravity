#include <iostream>
#include <string>
using namespace std;

class Shape {
public:
    virtual void display() = 0;
    virtual ~Shape() {}
};

class Circle : public Shape {
private:
    double radius;
public:
    Circle(double r) : radius(r) {}
    void display() override {
        cout << "Circle with radius " << radius << endl;
    }
    double area() const {
        return 3.14 * radius * radius;
    }
};

class Rectangle : public Shape {
private:
    double length, width;
public:
    Rectangle(double l, double w) : length(l), width(w) {}
    void display() override {
        cout << "Rectangle with length " << length << " and width " << width << endl;
    }
    double area() const {
        return length * width;
    }
};

template <typename T>
void processShape(Shape* ptr) {
    T* derived = dynamic_cast<T*>(ptr);
    if (derived) {
        cout << "Area: " << derived->area() << endl;
    } else {
        cout << "Invalid cast" << endl;
    }
}

int main() {
    string type, castType;
    cin >> type;
    
    Shape* shape = nullptr;
    
    if (type == "circle") {
        double radius;
        cin >> radius;
        shape = new Circle(radius);
    } else if (type == "rectangle") {
        double length, width;
        cin >> length >> width;
        shape = new Rectangle(length, width);
    }
    
    cin >> castType;
    
    if (castType == "circle") {
        processShape<Circle>(shape);
    } else if (castType == "rectangle") {
        processShape<Rectangle>(shape);
    }
    
    delete shape;
    return 0;
}
