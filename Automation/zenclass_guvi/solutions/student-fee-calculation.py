import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    idx = 0
    N = int(data[idx])
    idx += 1
    
    roll_numbers = []
    for _ in range(N):
        roll_numbers.append(int(data[idx]))
        idx += 1
    
    subjects = []
    for _ in range(N):
        subjects.append(data[idx])
        idx += 1
    
    student_subject = {}
    for i in range(N):
        student_subject[roll_numbers[i]] = subjects[i]
    
    M = int(data[idx])
    idx += 1
    
    subject_fee = {}
    for _ in range(M):
        subject = data[idx]
        fee = int(data[idx + 1])
        subject_fee[subject] = fee
        idx += 2
    
    results = []
    for roll in roll_numbers:
        subj = student_subject[roll]
        fee = subject_fee.get(subj, -1)
        results.append((roll, fee))
    
    results.sort(key=lambda x: x[0])
    
    for roll, fee in results:
        print(roll, fee)

if __name__ == "__main__":
    main()
