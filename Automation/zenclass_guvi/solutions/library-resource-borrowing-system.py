import sys

def main():
    outputs = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        
        if line.lower() == 'quit':
            outputs.append("Quitting the program.")
            break
        
        name = line
        try:
            status = input().strip()
        except EOFError:
            break
        
        try:
            title = input().strip()
        except EOFError:
            break
        
        if status.lower() == 'faculty':
            # Faculty can only borrow DVDs
            # Check if title contains "DVD"
            if 'DVD' in title:
                outputs.append(f'DVD "{title}" successfully borrowed by {name}.')
            else:
                outputs.append("Faculty members can only borrow DVDs.")
        elif status.lower() == 'student':
            # Students can borrow both books and DVDs
            if 'DVD' in title:
                outputs.append(f'DVD "{title}" successfully borrowed by {name}.')
            else:
                outputs.append(f'Book "{title}" successfully borrowed by {name}.')
    
    for output in outputs:
        print(output)

if __name__ == "__main__":
    main()
