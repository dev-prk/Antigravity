#include <iostream>
#include <string>
using namespace std;

class User {
public:
    void login(string name) {
        // login functionality - now protected due to protected inheritance
    }
protected:
    int accessLevel;
    void displayAccessLevel() {
        cout << "Access Level: " << accessLevel << endl;
    }
private:
    string password;
};

class Admin : protected User {
public:
    void adminLogin(string name, int level) {
        accessLevel = level;
        if (accessLevel >= 5) {
            cout << "Admin Logged In" << endl;
            displayAccessLevel();
        } else {
            cout << "Insufficient Privileges" << endl;
        }
    }
};

int main() {
    string name;
    int level;
    cin >> name;
    cin >> level;
    Admin a;
    a.adminLogin(name, level);
    return 0;
}
