#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    double real;
    double imaginary;
} ComplexNumber;

ComplexNumber add(ComplexNumber a, ComplexNumber b) {
    ComplexNumber result;
    result.real = a.real + b.real;
    result.imaginary = a.imaginary + b.imaginary;
    return result;
}

ComplexNumber subtract(ComplexNumber a, ComplexNumber b) {
    ComplexNumber result;
    result.real = a.real - b.real;
    result.imaginary = a.imaginary - b.imaginary;
    return result;
}

ComplexNumber multiply(ComplexNumber a, ComplexNumber b) {
    ComplexNumber result;
    result.real = a.real * b.real - a.imaginary * b.imaginary;
    result.imaginary = a.real * b.imaginary + a.imaginary * b.real;
    return result;
}

ComplexNumber divide(ComplexNumber a, ComplexNumber b) {
    ComplexNumber result;
    double denominator = b.real * b.real + b.imaginary * b.imaginary;
    if (denominator == 0) {
        result.real = 0;
        result.imaginary = 0;
        return result;
    }
    result.real = (a.real * b.real + a.imaginary * b.imaginary) / denominator;
    result.imaginary = (a.imaginary * b.real - a.real * b.imaginary) / denominator;
    return result;
}

void print_complex(ComplexNumber c, const char* op_name) {
    if (c.imaginary >= 0) {
        printf("%s: %.2f + %.2fi\n", op_name, c.real, c.imaginary);
    } else {
        printf("%s: %.2f - %.2fi\n", op_name, c.real, -c.imaginary);
    }
}

int main() {
    ComplexNumber c1, c2;
    
    if (scanf("%lf %lf", &c1.real, &c1.imaginary) != 2) {
        return 1;
    }
    
    if (scanf("%lf %lf", &c2.real, &c2.imaginary) != 2) {
        return 1;
    }
    
    ComplexNumber add_result = add(c1, c2);
    ComplexNumber sub_result = subtract(c1, c2);
    ComplexNumber mul_result = multiply(c1, c2);
    ComplexNumber div_result = divide(c1, c2);
    
    print_complex(add_result, "Addition");
    print_complex(sub_result, "Subtraction");
    print_complex(mul_result, "Multiplication");
    print_complex(div_result, "Division");
    
    return 0;
}
