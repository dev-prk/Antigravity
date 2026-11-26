import sys
import heapq
from collections import deque

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print(-1)
        return
    
    n = int(data[0])
    if n == 0:
        print(-1)
        return
    
    s = list(map(int, data[1:1+n]))
    
    beta_votes = 0
    gamma_votes = 0
    
    # Max heap: store (-strength, citizen_index, current_strength)
    heap = []
    for i in range(n):
        heapq.heappush(heap, (-s[i], i, s[i]))
    
    strengths = s[:]
    
    day = 0
    while beta_votes < 1000 or gamma_votes < 1000:
        day += 1
        
        # Beta picks once
        if beta_votes < 1000:
            # Find valid citizen with max current strength
            valid_found = False
            candidates = []
            
            while heap and not valid_found:
                neg_val, idx, stored_val = heapq.heappop(heap)
                current_str = strengths[idx]
                
                if current_str > 0 and current_str == stored_val:
                    beta_votes += current_str
                    new_str = current_str // 3
                    strengths[idx] = new_str
                    heapq.heappush(heap, (-new_str, idx, new_str))
                    valid_found = True
                else:
                    # Store for potential later use if still valid
                    if current_str > 0:
                        candidates.append((neg_val, idx, current_str))
            
            # Re-add candidates that might still be useful
            for neg_val, idx, stored_val in candidates:
                if strengths[idx] > 0:
                    heapq.heappush(heap, (-strengths[idx], idx, strengths[idx]))
        
        # Gamma picks twice
        if gamma_votes < 1000:
            for _ in range(2):
                if gamma_votes >= 1000:
                    break
                    
                valid_found = False
                candidates = []
                
                while heap and not valid_found:
                    neg_val, idx, stored_val = heapq.heappop(heap)
                    current_str = strengths[idx]
                    
                    if current_str > 0 and current_str == stored_val:
                        gamma_votes += current_str
                        new_str = current_str // 3
                        strengths[idx] = new_str
                        heapq.heappush(heap, (-new_str, idx, new_str))
                        valid_found = True
                    else:
                        if current_str > 0:
                            candidates.append((neg_val, idx, current_str))
                
                for neg_val, idx, stored_val in candidates:
                    if strengths[idx] > 0:
                        heapq.heappush(heap, (-strengths[idx], idx, strengths[idx]))
        
        # Safety check to avoid infinite loop
        if day > 10000:
            break
    
    if beta_votes >= 1000 and gamma_votes >= 1000:
        # Both reached 1000, whoever reached first wins
        # Since we process Beta first, if both reach in same day, Gamma wins
        print("Gamma")
    elif beta_votes >= 1000:
        print("Beta")
    elif gamma_votes >= 1000:
        print("Gamma")
    else:
        print(-1)

if __name__ == "__main__":
    main()
