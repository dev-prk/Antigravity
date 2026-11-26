import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    if N == 0:
        for _ in range(int(data[idx])):
            sys.stdout.write("NO\n")
        return
    
    H = []
    for _ in range(N):
        H.append(int(data[idx]))
        idx += 1
    
    P = int(data[idx])
    idx += 1
    
    next_greater = [N] * N
    stack = []
    for i in range(N):
        while stack and H[i] >= H[stack[-1]]:
            idx_pop = stack.pop()
            next_greater[idx_pop] = i
        stack.append(i)
    
    prev_greater = [-1] * N
    stack = []
    for i in range(N - 1, -1, -1):
        while stack and H[i] >= H[stack[-1]]:
            stack.pop()
        if stack:
            prev_greater[i] = stack[-1]
        else:
            prev_greater[i] = -1
        stack.append(i)
    
    queries = []
    for _ in range(P):
        L = int(data[idx]) - 1
        R = int(data[idx + 1]) - 1
        queries.append((L, R, _))
        idx += 2
    
    answers = ["NO"] * P
    
    for L, R, qidx in queries:
        if L == R:
            answers[qidx] = "YES"
        elif next_greater[L] > R:
            answers[qidx] = "YES"
        else:
            answers[qidx] = "NO"
    
    for ans in answers:
        sys.stdout.write(ans + "\n")

if __name__ == "__main__":
    main()
