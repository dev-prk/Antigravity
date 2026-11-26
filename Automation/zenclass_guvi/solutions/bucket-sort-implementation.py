import sys

def bucket_sort(arr, n):
    if n == 0:
        return []
    
    max_val = max(arr)
    min_val = min(arr)
    
    range_size = max_val - min_val + 1
    bucket_count = max(10, (range_size + 9) // 10)
    
    buckets = [[] for _ in range(bucket_count)]
    
    bucket_range = (range_size + bucket_count - 1) // bucket_count if bucket_count > 0 else 1
    
    for num in arr:
        if bucket_range == 0:
            bucket_idx = 0
        else:
            bucket_idx = (num - min_val) // bucket_range
            bucket_idx = min(bucket_idx, bucket_count - 1)
        buckets[bucket_idx].append(num)
    
    result = []
    for bucket in buckets:
        bucket.sort()
        result.extend(bucket)
    
    return result

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print("")
        return
    
    arr = list(map(int, data[1:n+1]))
    if len(arr) == 0:
        print("")
        return
    
    sorted_arr = bucket_sort(arr, n)
    print(' '.join(map(str, sorted_arr)))

if __name__ == "__main__":
    main()
