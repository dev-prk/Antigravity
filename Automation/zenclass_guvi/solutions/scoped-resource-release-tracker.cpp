#include <iostream>

class Resource {
private:
    static int count;
public:
    Resource() {
        count++;
        std::cout << "Object Created. Active: " << count << std::endl;
    }
    
    ~Resource() {
        count--;
        std::cout << "Object Destroyed. Active: " << count << std::endl;
    }
};

int Resource::count = 0;

int main() {
    int N;
    std::cin >> N;
    
    {
        Resource resources[N];
    }
    
    return 0;
}
