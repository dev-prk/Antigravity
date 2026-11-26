import sys
import math

data = sys.stdin.read().strip().split()
if len(data) < 2:
    sys.exit()

h = float(data[0])
w = float(data[1])

height_m = h / 100
bmi = w / (height_m * height_m)
bmi_rounded = round(bmi * 10 + 0.5) / 10

print("{0:.1f}".format(bmi_rounded))

if 19 <= bmi_rounded <= 25:
    print("Maintain your Current Diet Plan")
elif bmi_rounded < 19:
    print("Follow a Calorie Surplus Diet Plan")
else:
    print("Follow a Calorie Deficit Diet Plan")
