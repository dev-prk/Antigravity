#include <iostream>
#include <iomanip>
#include <string>
using namespace std;

class Product {
private:
    string productName;
    int productID;
    double price;
    int quantity;
public:
    void setDetails(string name, int id, double p, int q) {
        productName = name;
        productID = id;
        price = p;
        quantity = q;
    }
    
    double calculateTotalValue() {
        return price * quantity;
    }
    
    void display() {
        cout << "Product Name: " << productName << endl;
        cout << "Product ID: " << productID << endl;
        cout << fixed << setprecision(2);
        cout << "Price: " << price << endl;
        cout << "Quantity: " << quantity << endl;
        cout << "Total Value: " << calculateTotalValue() << endl;
    }
};

int main() {
    string productName;
    int productID, quantity;
    double price;
    
    cin >> productName >> productID >> price >> quantity;
    
    Product* productPtr = new Product();
    productPtr->setDetails(productName, productID, price, quantity);
    productPtr->display();
    
    delete productPtr;
    productPtr = nullptr;
    
    return 0;
}
