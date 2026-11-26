import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    
    n = int(data[0])
    if n == 0:
        print("")
        return
    
    usernames = data[1:n+1]
    count_map = {}
    result = []
    
    for username in usernames:
        if username not in count_map:
            count_map[username] = 1
            result.append("Verified")
        else:
            count_map[username] += 1
            result.append(username + str(count_map[username] - 1))
    
    print(" ".join(result))

if __name__ == "__main__":
    main()
