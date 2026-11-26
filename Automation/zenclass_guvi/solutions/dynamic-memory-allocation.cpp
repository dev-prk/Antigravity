#include <iostream>
#include <cstring>
using namespace std;

class StringRev {
private:
    char* sentence;
    int length;

public:
    // Parameterized constructor - dynamically allocates memory
    StringRev(const char* input) {
        length = strlen(input);
        sentence = new char[length + 1];
        strcpy(sentence, input);
    }

    // Function to reverse the sentence
    void reverse() {
        int start = 0;
        int end = length - 1;
        while (start < end) {
            char temp = sentence[start];
            sentence[start] = sentence[end];
            sentence[end] = temp;
            start++;
            end--;
        }
    }

    // Function to display the sentence
    void display() {
        cout << sentence;
    }

    // Destructor - deallocates memory
    ~StringRev() {
        delete[] sentence;
    }
};

int main() {
    string input;
    getline(cin, input);

    StringRev obj(input.c_str());
    obj.reverse();
    obj.display();

    return 0;
}
