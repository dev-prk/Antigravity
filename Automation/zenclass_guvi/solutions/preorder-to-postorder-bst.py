import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0])
    elements = list(map(int, data[1:1+n]))
    
    if n == 0:
        print("")
        return
    
    def build_postorder(pre, start, end):
        if start > end:
            return []
        root = pre[start]
        if start == end:
            return [root]
        
        partition = start + 1
        while partition <= end and pre[partition] < root:
            partition += 1
        
        left_part = build_postorder(pre, start + 1, partition - 1)
        right_part = build_postorder(pre, partition, end)
        
        return left_part + right_part + [root]
    
    postorder = build_postorder(elements, 0, n - 1)
    print(' '.join(map(str, postorder)), end=' \n')

if __name__ == "__main__":
    main()
