import sys

def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))
    
    if len(lines) == 0:
        print("")
        return
    elif len(lines) == 1:
        print(lines[0])
        return
    elif len(lines) == 2:
        sentence = lines[0]
        old_word = lines[1]
        new_word = ""
    else:
        sentence = lines[0]
        old_word = lines[1]
        new_word = lines[2]
    
    words = sentence.split()
    modified_words = []
    for word in words:
        if word == old_word:
            modified_words.append(new_word)
        else:
            modified_words.append(word)
    
    print(' '.join(modified_words))

if __name__ == "__main__":
    main()
