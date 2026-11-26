import bisect
import statistics

def minNumber(a, x):
    a_sorted = sorted(a)
    n = len(a_sorted)
    median = statistics.median(a_sorted)
    
    if median == x:
        return 0
    
    count = 0
    while statistics.median(a_sorted) != x:
        bisect.insort(a_sorted, x)
        count += 1
    
    return count

n = int(input())
a = list(map(int, input().split()))
x = int(input())
print(minNumber(a, x))
