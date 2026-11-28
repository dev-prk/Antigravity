import sys

def main():
    # Read number of available racks
    num_racks = int(sys.stdin.readline().strip())
    
    # Read number of book categories
    num_categories = int(sys.stdin.readline().strip())
    
    # Read book category details - store with original index
    categories = []
    for idx in range(num_categories):
        parts = sys.stdin.readline().strip().split()
        category_name = parts[0]
        book_available = int(parts[1])
        popularity = int(parts[2])
        categories.append((idx, category_name, book_available, popularity))
    
    # Sort categories by popularity in descending order (higher popularity first)
    sorted_categories = sorted(categories, key=lambda x: -x[3])
    
    # Allocate racks prioritizing higher popularity
    allocation = []
    racks_used = 0
    
    for idx, category_name, book_available, popularity in sorted_categories:
        if racks_used >= num_racks:
            break
        
        # Each rack can hold up to 10 books
        needed_racks = (book_available + 9) // 10
        available_racks = num_racks - racks_used
        racks_allocated = min(needed_racks, available_racks)
        
        if racks_allocated > 0:
            allocation.append((idx, category_name, racks_allocated))
            racks_used += racks_allocated
    
    # Sort by original input order and output
    allocation.sort(key=lambda x: x[0])
    
    for idx, category_name, racks_allocated in allocation:
        print(f"{category_name} {racks_allocated}")

if __name__ == "__main__":
    main()
