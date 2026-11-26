#include <iostream>

namespace Internal {
    int marks(int m1, int m2) {
        return m1 + m2;
    }
}

namespace External {
    int marks(int m1, int m2) {
        return m1 + m2;
    }
}

int main() {
    using namespace std;
    
    int internal1, internal2;
    int external1, external2;
    
    cin >> internal1 >> internal2;
    cin >> external1 >> external2;
    
    int internalTotal = Internal::marks(internal1, internal2);
    int externalTotal = External::marks(external1, external2);
    int grandTotal = internalTotal + externalTotal;
    
    cout << "Internal Total: " << internalTotal << endl;
    cout << "External Total: " << externalTotal << endl;
    cout << "Grand Total: " << grandTotal << endl;
    
    return 0;
}
