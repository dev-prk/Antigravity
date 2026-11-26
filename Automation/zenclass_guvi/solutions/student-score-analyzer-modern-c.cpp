#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <iomanip>
#include <algorithm>

struct Student {
    std::string name;
    double average_score;
};

int main() {
    int n;
    std::cin >> n;
    
    std::unordered_map<std::string, std::pair<int, double>> score_map;
    
    for (int i = 0; i < n; ++i) {
        std::string name;
        double score;
        std::cin >> name >> score;
        score_map[name].first++;
        score_map[name].second += score;
    }
    
    std::vector<Student> students;
    for (const auto& entry : score_map) {
        Student s;
        s.name = entry.first;
        s.average_score = entry.second.second / entry.second.first;
        students.push_back(s);
    }
    
    std::sort(students.begin(), students.end(), [](const Student& a, const Student& b) {
        if (a.average_score != b.average_score) {
            return a.average_score > b.average_score;
        }
        return a.name < b.name;
    });
    
    std::cout << "Sorted List:" << std::endl;
    for (const auto& student : students) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << student.name << " " << student.average_score << std::endl;
    }
    
    if (!students.empty()) {
        std::cout << "Top Scorer: " << students[0].name << std::endl;
    }
    
    return 0;
}
