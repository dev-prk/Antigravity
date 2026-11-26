#include <iostream>
#include <iomanip>
using namespace std;

class Box {
private:
    double length;
    double breadth;
    double height;
    
public:
    void setDimensions(double l, double b, double h) {
        length = l;
        breadth = b;
        height = h;
    }
    
    void setDimensions(double side) {
        length = side;
        breadth = side;
        height = side;
    }
    
    double calculateVolume() {
        return length * breadth * height;
    }
    
    friend void compareBoxes(Box b1, Box b2);
};

void compareBoxes(Box b1, Box b2) {
    double vol1 = b1.calculateVolume();
    double vol2 = b2.calculateVolume();
    
    if (vol1 > vol2) {
        cout << "Box 1 is larger" << endl;
    } else if (vol2 > vol1) {
        cout << "Box 2 is larger" << endl;
    } else {
        cout << "Both boxes are equal in volume" << endl;
    }
}

int main() {
    Box box1, box2;
    
    int type1;
    cin >> type1;
    if (type1 == 1) {
        double l, b, h;
        cin >> l >> b >> h;
        box1.setDimensions(l, b, h);
    } else if (type1 == 2) {
        double side;
        cin >> side;
        box1.setDimensions(side);
    }
    
    int type2;
    cin >> type2;
    if (type2 == 1) {
        double l, b, h;
        cin >> l >> b >> h;
        box2.setDimensions(l, b, h);
    } else if (type2 == 2) {
        double side;
        cin >> side;
        box2.setDimensions(side);
    }
    
    cout << fixed << setprecision(2);
    cout << "Volume of Box 1: " << box1.calculateVolume() << endl;
    cout << "Volume of Box 2: " << box2.calculateVolume() << endl;
    
    compareBoxes(box1, box2);
    
    return 0;
}
