#include <stdio.h>
#include <stdlib.h>

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
    result.real = (a.real * b.real + a.imaginary * b.imaginary) / denominator;
    result.imaginary = (a.imaginary * b.real - a.real * b.imaginary) / denominator;
    return result;
}

void printComplex(ComplexNumber c) {
    if (c.imaginary >= 0) {
        printf("%.2f + %.2fi", c.real, c.imaginary);
    } else {
        printf("%.2f - %.2fi", c.real, -c.imaginary);
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
    
    ComplexNumber sum = add(c1, c2);
    ComplexNumber diff = subtract(c1, c2);
    ComplexNumber prod = multiply(c1, c2);
    ComplexNumber quot = divide(c1, c2);
    
    printf("Addition: ");
    printComplex(sum);
    printf("\n");
    
    printf("Subtraction: ");
    printComplex(diff);
    printf("\n");
    
    printf("Multiplication: ");
    printComplex(prod);
    printf("\n");
    
    printf("Division: ");
    printComplex(quot);
    printf("\n");
    
    return 0;
}
