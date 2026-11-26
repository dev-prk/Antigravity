import sys

def main():
    data = sys.stdin.read().strip().split()
    if len(data) < 2:
        return
    try:
        N = int(data[0])
        X = int(data[1])
    except ValueError:
        return
    
    if N <= 0:
        print(0)
        return
    
    # The last person arrives at time (N-1)*X
    arrival_time = (N - 1) * X
    
    # The service starts at the end of all previous services
    # Total service time for (N-1) cars before last person is (N-1)*10
    service_end = (N - 1) * 10
    
    # Waiting time is the difference
    waiting_time = service_end - arrival_time
    
    print(waiting_time)

if __name__ == "__main__":
    main()
