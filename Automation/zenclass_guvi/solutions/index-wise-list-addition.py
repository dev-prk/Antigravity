import sys

def main():
    data = sys.stdin.read().split()
    if len(data) < 2:
        return
    try:
        n1 = int(data[0])
        n2 = int(data[1])
    except ValueError:
        return
    if n1 < 0:
        n1 = 0
    if n2 < 0:
        n2 = 0
    list1 = data[2:2 + n1]
    list2 = data[2 + n1:2 + n1 + n2]
    res = []
    m = min(len(list1), len(list2))
    for i in range(m):
        res.append(list1[i] + list2[i])
    res.extend(list1[m:])
    res.extend(list2[m:])
    print(' '.join(res))

if __name__ == '__main__':
    main()
