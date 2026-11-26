import sys

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    
    idx = 0
    n = int(data[idx])
    idx += 1
    
    word_set = set()
    for _ in range(n):
        word = data[idx].strip()
        word_set.add(word)
        idx += 1
    
    q = int(data[idx])
    idx += 1
    
    results = []
    for _ in range(q):
        line = data[idx].strip()
        idx += 1
        parts = line.split()
        if not parts:
            results.append("All words in list")
            continue
        
        count = int(parts[0])
        words_in_sentence = parts[1:1+count]
        
        all_in_list = True
        for word in words_in_sentence:
            if word not in word_set:
                all_in_list = False
                break
        
        if all_in_list:
            results.append("Not all words in list")
        else:
            results.append("All words in list")
    
    for res in results:
        print(res)

if __name__ == "__main__":
    main()
