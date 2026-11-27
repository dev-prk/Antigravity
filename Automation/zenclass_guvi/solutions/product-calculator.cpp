#include <iostream>
#include <sstream>
#include <string>
#include <cmath>
#include <iomanip>
#include <limits>
#include <vector>

class ProductCalculator {
private:
    double a, b;
    double product;

public:
    ProductCalculator(double x, double y) : a(x), b(y) {
        product = a * b;
    }

    double getProduct() const {
        return product;
    }

    int getPrecision(double val) const {
        std::ostringstream oss;
        oss << std::fixed << val;
        std::string str = oss.str();
        
        size_t dotPos = str.find('.');
        if (dotPos == std::string::npos) {
            return 0;
        }
        
        std::string decimalPart = str.substr(dotPos + 1);
        int trailingZeros = 0;
        for (int i = decimalPart.size() - 1; i >= 0; i--) {
            if (decimalPart[i] == '0') {
                trailingZeros++;
            } else {
                break;
            }
        }
        
        int effectiveDecimals = decimalPart.size() - trailingZeros;
        return effectiveDecimals;
    }
};

int main() {
    std::vector<ProductCalculator> products;
    double total = 0.0;
    int maxPrecision = 0;
    
    for (int i = 0; i < 3; i++) {
        double x, y;
        std::cin >> x >> y;
        ProductCalculator pc(x, y);
        total += pc.getProduct();
        
        int prec_x = pc.getPrecision(x);
        int prec_y = pc.getPrecision(y);
        int prec_p = pc.getPrecision(pc.getProduct());
        
        int local_max = prec_x > prec_y ? prec_x : prec_y;
        local_max = local_max > prec_p ? local_max : prec_p;
        
        if (local_max > maxPrecision) {
            maxPrecision = local_max;
        }
    }
    
    if (maxPrecision == 0) {
        std::cout << static_cast<long long>(round(total)) << std::endl;
    } else if (maxPrecision <= 2) {
        std::cout << std::fixed << std::setprecision(2) << round(total * 100) / 100 << std::endl;
    } else {
        std::cout << std::fixed << std::setprecision(6) << round(total * 1000000) / 1000000 << std::endl;
    }
    
    return 0;
}
