#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Array {
private:
    int* data;
    int size;

public:
    Array() : data(nullptr), size(0) {}

    Array(int n) : size(n) {
        if (n <= 0) {
            data = nullptr;
            size = 0;
        } else {
            data = new int[n];
        }
    }

    Array(const Array& other) : size(other.size) {
        if (size <= 0) {
            data = nullptr;
        } else {
            data = new int[size];
            for (int i = 0; i < size; ++i) {
                data[i] = other.data[i];
            }
        }
    }

    ~Array() {
        delete[] data;
    }

    void readElements() {
        if (size > 0) {
            for (int i = 0; i < size; ++i) {
                cin >> data[i];
            }
        }
    }

    void modifyFirst(int value) {
        if (size > 0) {
            data[0] = value;
        }
    }

    void display() {
        if (size == 0) {
            cout << "";
            return;
        }
        for (int i = 0; i < size; ++i) {
            if (i > 0) {
                cout << " ";
            }
            cout << data[i];
        }
    }

    int getSize() const {
        return size;
    }
};

int main() {
    int n;
    cin >> n;
    
    Array a1(n);
    a1.readElements();
    
    Array a2(a1);
    
    int modifyValue;
    cin >> modifyValue;
    a1.modifyFirst(modifyValue);
    
    cout << "Original: ";
    a1.display();
    cout << " " << endl;
    
    cout << "Clone: ";
    a2.display();
    cout << " " << endl;
    
    return 0;
}
