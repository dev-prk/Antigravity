#include <iostream>
#include <string>

class Complex {
public:
    int real;
    int imag;
    
    Complex(int r = 0, int i = 0) : real(r), imag(i) {}
    
    Complex operator+(const Complex& other) const {
        return Complex(real + other.real, imag + other.imag);
    }
    
    Complex operator-(const Complex& other) const {
        return Complex(real - other.real, imag - other.imag);
    }
    
    Complex operator*(const Complex& other) const {
        return Complex(real * other.real - imag * other.imag, 
                       real * other.imag + imag * other.real);
    }
};

std::ostream& operator<<(std::ostream& os, const Complex& c) {
    os << c.real << " + " << c.imag << "i";
    return os;
}

int main() {
    int a, b, c, d;
    std::cin >> a >> b >> c >> d;
    
    Complex c1(a, b);
    Complex c2(c, d);
    
    Complex sum = c1 + c2;
    Complex diff = c1 - c2;
    Complex prod = c1 * c2;
    
    std::cout << "Addition: " << sum << std::endl;
    std::cout << "Subtraction: " << diff << std::endl;
    std::cout << "Multiplication: " << prod << std::endl;
    
    return 0;
}
