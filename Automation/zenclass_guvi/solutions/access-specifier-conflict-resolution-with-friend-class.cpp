#include <iostream>
#include <string>

class Vault {
private:
    std::string password;
protected:
    int vaultID;

public:
    Vault() : vaultID(0) {}

    void setVaultID(int id) {
        vaultID = id;
    }

    void setPassword(const std::string& pwd) {
        password = pwd;
    }

    std::string getPassword() const {
        return password;
    }

    void open() const {
        std::cout << "Vault opened" << std::endl;
    }

    friend class Auditor;
};

class SecureVault : protected Vault {
public:
    void accessOpen() {
        open();
    }
};

class Auditor {
public:
    void audit(Vault& v, const std::string& inputPassword) {
        if (v.getPassword() == inputPassword) {
            std::cout << "Vault " << v.vaultID << " Audit Successful" << std::endl;
        } else {
            std::cout << "Audit Failed" << std::endl;
        }
    }
};

int main() {
    int vaultID;
    std::string password;
    std::string inputPassword;

    std::cin >> vaultID >> password >> inputPassword;

    Vault v;
    v.setVaultID(vaultID);
    v.setPassword(password);

    Auditor auditor;
    auditor.audit(v, inputPassword);

    return 0;
}
