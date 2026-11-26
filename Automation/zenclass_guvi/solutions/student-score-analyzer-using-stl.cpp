#include <iostream>
#include <vector>
#include <map>
#include <algorithm>
#include <string>

int main() {
    int n;
    std::cin >> n;
    
    std::map<std::string, int> studentScores;
    std::vector<int> scores;
    
    for (int i = 0; i < n; ++i) {
        std::string name;
        int score;
        std::cin >> name >> score;
        studentScores[name] = score;
        scores.push_back(score);
    }
    
    // Sort scores in ascending order
    std::sort(scores.begin(), scores.end());
    
    // Output sorted scores
    std::cout << "Sorted Scores: ";
    for (size_t i = 0; i < scores.size(); ++i) {
        if (i > 0) std::cout << " ";
        std::cout << scores[i];
    }
    std::cout << " \n";
    
    // Find highest score
    int highest = scores.back();
    std::cout << "Highest Score: " << highest << "\n";
    
    // Find lowest score
    int lowest = scores.front();
    std::cout << "Lowest Score: " << lowest << "\n";
    
    // Count students above 75
    int countAbove75 = 0;
    for (int score : scores) {
        if (score > 75) {
            countAbove75++;
        }
    }
    std::cout << "Students above 75: " << countAbove75 << "\n";
    
    return 0;
}
