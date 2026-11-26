import sys

def main():
    data = sys.stdin.readline().split()
    a = int(data[0])
    b = int(data[1])
    f = int(data[2])
    k = int(data[3])
    
    if k == 0:
        print(0)
        return
    
    fuel = b
    refuels = 0
    
    for journey in range(k):
        if journey % 2 == 0:
            start_to_f = f
            f_to_end = a - f
        else:
            start_to_f = a - f
            f_to_end = f
        
        fuel -= start_to_f
        fuel -= f_to_end
        
        if journey < k - 1:
            if journey % 2 == 0:
                next_start_to_f = f
                next_f_to_end = a - f
            else:
                next_start_to_f = a - f
                next_f_to_end = f
            
            total_next_leg = next_start_to_f + next_f_to_end
            
            if fuel < total_next_leg:
                if fuel < next_start_to_f:
                    print(-1)
                    return
                fuel = b - total_next_leg
                refuels += 1
            else:
                fuel -= total_next_leg
    
    print(refuels)

if __name__ == "__main__":
    main()
