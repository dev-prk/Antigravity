import sys

def can_allocate(books, num_students, max_pages):
    students_needed = 1
    current_pages = 0
    
    for pages in books:
        if pages > max_pages:
            return False
        
        if current_pages + pages <= max_pages:
            current_pages += pages
        else:
            students_needed += 1
            current_pages = pages
            
            if students_needed > num_students:
                return False
    
    return True

def minimize_max_pages(books, num_students):
    if num_students > len(books):
        return -1
    
    if num_students == len(books):
        return max(books)
    
    low = max(books)
    high = sum(books)
    result = -1
    
    while low <= high:
        mid = (low + high) // 2
        
        if can_allocate(books, num_students, mid):
            result = mid
            high = mid - 1
        else:
            low = mid + 1
    
    return result

def main():
    data = sys.stdin.read().strip().split()
    
    if not data:
        print(-1)
        return
    
    num_books = int(data[0])
    
    pages = []
    for i in range(1, num_books + 1):
        pages.append(int(data[i]))
    
    num_students = int(data[num_books + 1])
    
    result = minimize_max_pages(pages, num_students)
    print(result)

if __name__ == "__main__":
    main()
