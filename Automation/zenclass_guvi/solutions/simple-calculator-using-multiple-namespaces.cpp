#include <iostream>
using namespace std;

namespace Arithmetic {
    int operate(int a, int b) {
        return a + b;
    }
}

namespace Advanced {
    int operate(int a, int b) {
        return a * b;
    }
    
    namespace Power {
        int operate(int base, int exp) {
            int result = 1;
            for (int i = 0; i < exp; i++) {
                result *= base;
            }
            return result;
        }
    }
}

int main() {
    int a, b, base, exp;
    cin >> a >> b;
    cin >> base >> exp;
    
    cout << "Addition: " << Arithmetic::operate(a, b) << endl;
    cout << "Multiplication: " << Advanced::operate(a, b) << endl;
    cout << "Power: " << Advanced::Power::operate(base, exp) << endl;
    
    return 0;
}
