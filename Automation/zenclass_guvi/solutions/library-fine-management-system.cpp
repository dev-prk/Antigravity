#include <iostream>
#include <string>
#include <iomanip>

class LibraryBook {
private:
    std::string bookTitle;
    int bookID;
    int daysLate;
    double fineAmount;

public:
    void setDetails(std::string title, int id, int lateDays) {
        bookTitle = title;
        bookID = id;
        daysLate = lateDays;
    }

    void calculateFine() {
        if (daysLate <= 5) {
            fineAmount = daysLate * 2.0;
        } else {
            fineAmount = 5.0 * 5 + (daysLate - 5) * 5.0;
        }
    }

    void display() {
        std::cout << "Book Title: " << bookTitle << std::endl;
        std::cout << "Book ID: " << bookID << std::endl;
        std::cout << "Days Late: " << daysLate << std::endl;
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Fine: " << fineAmount << std::endl;
    }
};

int main() {
    LibraryBook book;
    std::string title;
    int id, days;
    
    std::cin >> title >> id >> days;
    
    book.setDetails(title, id, days);
    book.calculateFine();
    book.display();
    
    return 0;
}
