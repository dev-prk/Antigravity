import sys

def main():
    G = sys.stdin.readline().strip()
    if not G:
        Q = int(sys.stdin.readline().strip())
        for _ in range(Q):
            sys.stdin.readline()
            print("NO")
        return
    
    Q = int(sys.stdin.readline().strip())
    
    for _ in range(Q):
        H = sys.stdin.readline().strip()
        if not H:
            print("NO")
            continue
        
        H_rev = H[::-1]
        h_len = len(H_rev)
        g_len = len(G)
        
        if g_len < h_len - 1:
            print("NO")
            continue
        
        # Check if H_rev is a suffix of G
        if G[-h_len:] == H_rev:
            remaining = G[:g_len - h_len + 1]
            if remaining == H:
                print("YES")
            else:
                print("NO")
        else:
            print("NO")

if __name__ == "__main__":
    main()
