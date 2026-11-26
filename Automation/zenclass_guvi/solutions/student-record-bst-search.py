import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print("Not Found")
        return
    
    n = int(data[0])
    if n == 0:
        print("Not Found")
        return
    
    nums = list(map(int, data[1:1+n]))
    target = int(data[1+n])
    
    root = None
    for num in nums:
        root = insert(root, num)
    
    if search(root, target):
        print("Found")
    else:
        print("Not Found")

def insert(root, val):
    if root is None:
        return {'data': val, 'left': None, 'right': None}
    if val < root['data']:
        root['left'] = insert(root['left'], val)
    else:
        root['right'] = insert(root['right'], val)
    return root

def search(root, target):
    if root is None:
        return False
    if root['data'] == target:
        return True
    if target < root['data']:
        return search(root['left'], target)
    return search(root['right'], target)

if __name__ == "__main__":
    main()
