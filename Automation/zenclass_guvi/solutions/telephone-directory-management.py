import sys

def main():
    data = sys.stdin.read().strip().splitlines()
    if not data:
        return
    
    n = int(data[0].strip())
    directory = []
    index = 1
    
    for i in range(n):
        if index >= len(data):
            break
        line = data[index].strip()
        index += 1
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            tel = parts[1]
            directory.append([name, tel])
    
    if index >= len(data):
        return
    
    op = int(data[index].strip())
    index += 1
    
    if index >= len(data):
        return
    
    line = data[index].strip()
    
    if op == 1:
        if line:
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                tel = parts[1]
                directory.append([name, tel])
        for entry in directory:
            print(entry[0], entry[1])
    
    elif op == 2:
        if line:
            parts = line.split()
            if len(parts) >= 3:
                old_tel = parts[0]
                new_name = parts[1]
                new_tel = parts[2]
                for entry in directory:
                    if entry[1] == old_tel:
                        entry[0] = new_name
                        entry[1] = new_tel
                        break
                for entry in directory:
                    print(entry[0], entry[1])
    
    elif op == 3:
        if line:
            parts = line.split()
            if len(parts) >= 1:
                del_tel = parts[0]
                for i, entry in enumerate(directory):
                    if entry[1] == del_tel:
                        del directory[i]
                        break
                for entry in directory:
                    print(entry[0], entry[1])

if __name__ == "__main__":
    main()
