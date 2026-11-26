#include <iostream>
#include <string>
#include <cmath>
#include <iomanip>

class Shape {
public:
    virtual double area() = 0;
    virtual double perimeter() = 0;
    virtual ~Shape() = default;
};

class Rectangle : public Shape {
private:
    double length, width;
public:
    Rectangle(double l, double w) : length(l), width(w) {}
    
    double area() override {
        return length * width;
    }
    
    double perimeter() override {
        return 2 * (length + width);
    }
};

class Circle : public Shape {
private:
    double radius;
public:
    Circle(double r) : radius(r) {}
    
    double area() override {
        return M_PI * radius * radius;
    }
    
    double perimeter() override {
        return 2 * M_PI * radius;
    }
};

int main() {
    std::string shapeType;
    std::cin >> shapeType;
    
    Shape* shape = nullptr;
    
    if (shapeType == "Rectangle") {
        double length, width;
        std::cin >> length >> width;
        shape = new Rectangle(length, width);
    } else if (shapeType == "Circle") {
        double radius;
        std::cin >> radius;
        shape = new Circle(radius);
    }
    
    if (shape) {
        std::cout << std::fixed << std::setprecision(1);
        std::cout << "Area: " << shape->area() << std::endl;
        std::cout << "Perimeter: " << shape->perimeter() << std::endl;
        delete shape;
    }
    
    return 0;
}
