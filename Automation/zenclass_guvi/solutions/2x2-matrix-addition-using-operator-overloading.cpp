#include <iostream>
#include <vector>

class Matrix {
private:
    int mat[2][2];

public:
    Matrix() {
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                mat[i][j] = 0;
            }
        }
    }

    Matrix(int a, int b, int c, int d) {
        mat[0][0] = a;
        mat[0][1] = b;
        mat[1][0] = c;
        mat[1][1] = d;
    }

    Matrix operator+(const Matrix& other) {
        Matrix result;
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                result.mat[i][j] = mat[i][j] + other.mat[i][j];
            }
        }
        return result;
    }

    void display() {
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                std::cout << mat[i][j];
                if (j == 0) {
                    std::cout << " ";
                }
            }
            std::cout << std::endl;
        }
    }
};

int main() {
    int a1, a2, a3, a4;
    int b1, b2, b3, b4;

    std::cin >> a1 >> a2 >> a3 >> a4;
    std::cin >> b1 >> b2 >> b3 >> b4;

    Matrix A(a1, a2, a3, a4);
    Matrix B(b1, b2, b3, b4);

    Matrix C = A + B;
    C.display();

    return 0;
}
