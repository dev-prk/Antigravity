import sys
import heapq
from collections import defaultdict

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("0 0")
        return
    
    idx = 0
    N = int(data[idx])
    Q = int(data[idx + 1])
    idx += 2
    
    P = list(map(int, data[idx:idx + N]))
    idx += N
    
    # Use a min-heap to track prices
    heap = []
    for price in P:
        heapq.heappush(heap, price)
    
    bought_count = 0
    total_spent = 0
    
    # Track current prices
    current_prices = P[:]
    
    for _ in range(Q):
        query_type = int(data[idx])
        idx += 1
        
        if query_type == 1:
            X = int(data[idx])
            idx += 1
            
            # Find the minimum price in the heap
            min_price = heap[0] if heap else None
            
            if min_price is not None:
                # Update all occurrences of min_price
                new_min_price = min_price + X
                if new_min_price < 0:
                    new_min_price = 0
                
                # Remove old min_price and add new price
                # We need to rebuild the heap after updates
                new_heap = []
                count_updated = 0
                while heap:
                    price = heapq.heappop(heap)
                    if price == min_price and count_updated < current_prices.count(min_price):
                        heapq.heappush(new_heap, new_min_price)
                        count_updated += 1
                    else:
                        heapq.heappush(new_heap, price)
                heap = new_heap
                
                # Update current_prices
                for i in range(len(current_prices)):
                    if current_prices[i] == min_price:
                        current_prices[i] = new_min_price
        
        elif query_type == 2:
            if heap:
                price = heapq.heappop(heap)
                bought_count += 1
                total_spent += price
                # Don't push back since we're buying it
                # The problem says we buy at current price, so price decreases
                # But wait - we need to push back the decremented version?
                # Actually, re-reading: "The prices of the perfume of the available N brands is given"
                # Each purchase consumes one unit, but supply is infinite
                # So we don't remove it from availability
                heapq.heappush(heap, price)
    
    print(f"{bought_count} {total_spent}")

if __name__ == "__main__":
    main()
