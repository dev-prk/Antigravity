#include <iostream>
#include <cstring>
using namespace std;

class DynamicString {
private:
    char* data;
    size_t length;

public:
    // Default constructor
    DynamicString() : data(nullptr), length(0) {
        data = new char[1];
        data[0] = '\0';
        length = 0;
    }

    // Constructor with initial string
    DynamicString(const char* str) {
        length = strlen(str);
        data = new char[length + 1];
        strcpy(data, str);
    }

    // Copy constructor
    DynamicString(const DynamicString& other) {
        length = other.length;
        data = new char[length + 1];
        strcpy(data, other.data);
    }

    // Assignment operator overloading
    DynamicString& operator=(const DynamicString& other) {
        if (this == &other) {
            return *this;
        }
        
        delete[] data;
        
        length = other.length;
        data = new char[length + 1];
        strcpy(data, other.data);
        
        return *this;
    }

    // Assignment operator for C-style string
    DynamicString& operator=(const char* str) {
        if (data != nullptr) {
            delete[] data;
        }
        
        length = strlen(str);
        data = new char[length + 1];
        strcpy(data, str);
        
        return *this;
    }

    // Print the string
    void print() const {
        cout << data;
    }

    // Get the underlying data
    const char* c_str() const {
        return data;
    }

    // Destructor
    ~DynamicString() {
        delete[] data;
    }
};

int main() {
    DynamicString str1, str2;
    
    char temp1[256], temp2[256];
    cin >> temp1 >> temp2;
    
    str1 = temp1;  // Assign first string
    str2 = temp2;  // Assign second string
    
    str1 = str2;   // Assign second string to first via operator=
    
    cout << "After Assignment: ";
    str1.print();
    cout << endl;
    
    return 0;
}
