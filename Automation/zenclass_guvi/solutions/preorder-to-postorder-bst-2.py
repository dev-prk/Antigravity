import sys

def main():
    line = sys.stdin.readline()
    if not line or not line.strip():
        return
    preorder = list(map(int, line.split()))
    
    if not preorder:
        return
    
    def build_postorder(pre, start, end):
        if start >= end:
            return []
        
        root = pre[start]
        
        i = start + 1
        while i < end and pre[i] < root:
            i += 1
        
        left_post = build_postorder(pre, start + 1, i)
        right_post = build_postorder(pre, i, end)
        
        return left_post + right_post + [root]
    
    postorder = build_postorder(preorder, 0, len(preorder))
    print(' '.join(map(str, postorder)))

if __name__ == "__main__":
    main()
