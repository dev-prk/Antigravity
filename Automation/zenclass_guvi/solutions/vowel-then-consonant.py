import sys

def main():
    s = sys.stdin.readline().strip()
    if not s:
        print()
        return
    
    vowels = set('aeiouAEIOU')
    vow = []
    cons = []
    for ch in s:
        if ch.isalpha():
            if ch in vowels:
                vow.append(ch)
            else:
                cons.append(ch)
    # Non-alphabetic characters: problem says vowels then consonants. 
    # But examples only have letters. Let's assume all characters are letters.
    # To be safe, if input has non-letters, the problem is ambiguous. 
    # Given the problem statement "print the vowels first and then consonants", 
    # it implies only vowels and consonants matter. But the input might have 
    # other chars? The sample inputs are pure letters. N <= 10000.
    # Let's stick to the straightforward interpretation: separate vowels and consonants.
    result = ''.join(vow) + ''.join(cons)
    print(result)

if __name__ == '__main__':
    main()
