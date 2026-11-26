p, q = input().split()
res = []
n, m = len(p), len(q)
min_len = min(n, m)
for i in range(min_len):
    res.append(p[i])
    res.append(q[i])
nums = []
for i in range(1, max(n, m) - min_len + 1):
    nums.append(str(i))
# Interleave remaining letters and numbers
rest_p = p[min_len:]
rest_q = q[min_len:]
all_rest = []
max_rest = max(len(rest_p), len(rest_q), len(nums))
for i in range(max_rest):
    if i < len(rest_p):
        all_rest.append(rest_p[i])
    if i < len(nums):
        all_rest.append(nums[i])
    if i < len(rest_q):
        all_rest.append(rest_q[i])
print(''.join(res + all_rest))
