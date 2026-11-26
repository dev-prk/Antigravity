import sys

def main():
    total_classes = int(sys.stdin.readline().strip())
    attended_classes = int(sys.stdin.readline().strip())
    
    missed_classes = total_classes - attended_classes
    
    if total_classes == 0:
        attendance_percentage = 0
    else:
        attendance_percentage = (attended_classes / total_classes) * 100
    
    attendance_percentage = int(attendance_percentage)
    
    if attendance_percentage >= 75:
        eligibility = "Eligible"
    else:
        eligibility = "Not Eligible"
    
    print(f"Attendance Percentage: {attendance_percentage}")
    print(f"Missed Classes: {missed_classes}")
    print(f"Eligibility: {eligibility}")

if __name__ == "__main__":
    main()
