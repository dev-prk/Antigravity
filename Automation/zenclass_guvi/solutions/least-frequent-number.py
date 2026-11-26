from collections import Counter
import sys

input = sys.stdin.read
data = input().split()

N = int(data[0])
numbers = list(map(int, data[1:]))

freq_counter = Counter(numbers)
min_freq = min(freq_counter.values())
least_frequent_numbers = [num for num, freq in freq_counter.items() if freq == min_freq]

print(min(least_frequent_numbers))
