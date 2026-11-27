#include <iostream>
#include <unordered_map>
#include <set>
#include <queue>
#include <algorithm>
#include <string>
#include <vector>
#include <sstream>

using namespace std;

int main() {
    int n;
    cin >> n;
    cin.ignore(); // Consume the newline after reading n
    
    unordered_map<string, int> productMap;
    set<string> productSet;
    priority_queue<int> priceQueue;
    vector<int> prices;
    
    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);
        
        istringstream iss(line);
        string productName;
        int price;
        
        iss >> productName >> price;
        
        // Handle duplicates: if product exists, remove old price from queue
        if (productMap.find(productName) != productMap.end()) {
            // Note: We can't efficiently remove from priority_queue, but we can
            // handle this in the counting phase
        }
        
        productSet.insert(productName);
        productMap[productName] = price;
        priceQueue.push(price);
        prices.push_back(price);
    }
    
    // Display all product names in alphabetical order (using set)
    cout << "Products (sorted): ";
    for (const string& name : productSet) {
        cout << name << " ";
    }
    cout << endl;
    
    // Display the most expensive product price (using priority_queue)
    cout << "Highest Price: " << priceQueue.top() << endl;
    
    // Count how many products cost more than 1000 (using algorithm)
    int count = 0;
    for (const auto& pair : productMap) {
        if (pair.second > 1000) {
            count++;
        }
    }
    cout << "Products above 1000: " << count << endl;
    
    return 0;
}
