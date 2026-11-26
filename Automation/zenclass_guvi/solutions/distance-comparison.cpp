#include <iostream>
using namespace std;

class Distance {
private:
    int meters;
public:
    Distance(int m) : meters(m) {}
    
    friend bool operator>(const Distance& d1, const Distance& d2) {
        return d1.meters > d2.meters;
    }
};

int main() {
    int a, b;
    cin >> a >> b;
    Distance d1(a), d2(b);
    if (d1 > d2) {
        cout << "First is Greater" << endl;
    } else {
        cout << "Second is Greater" << endl;
    }
    return 0;
}
