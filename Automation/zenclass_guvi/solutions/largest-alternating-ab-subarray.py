import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        print(0)
        return
    # The input might have a single line
    parts = data.split()
    if not parts:
        print(0)
        return
    s = parts[0]
    
    n = len(s)
    if n == 0:
        print(0)
        return
    
    # Find the largest subarray that alternates between 'a' and 'b'
    # The subarray must consist only of 'a' and 'b' characters? Let's check.
    # "alternating 'ab' subarray" - typically means a contiguous subsequence
    # where characters alternate between 'a' and 'b'.
    # But what if there are other characters? They would break the alternation.
    # Also, the subarray should consist only of 'a' and 'b'.
    
    # Let's find the longest contiguous subsequence where:
    # 1. All characters are 'a' or 'b'
    # 2. Consecutive characters alternate (s[i] != s[i+1])
    
    max_len = 0
    current_len = 0
    prev_char = ''
    
    for i in range(n):
        c = s[i]
        if c != 'a' and c != 'b':
            # Break the current sequence
            current_len = 0
            prev_char = ''
            continue
        
        if current_len == 0:
            # Start a new sequence
            current_len = 1
            prev_char = c
        else:
            if c == prev_char:
                # Reset to just this character
                current_len = 1
                prev_char = c
            else:
                current_len += 1
                prev_char = c
        
        if current_len > max_len:
            max_len = current_len
    
    # If max_len is 1, that's a valid alternating subarray of length 1
    # But wait, do we need at least 2 characters? Let's check with examples.
    # Sample 3: aaaabbbbaaaabbbbaaaa -> output 2. 
    # The alternating parts: at the boundary between a's and b's, we get "ab" or "ba" of length 2.
    # So length 1 should not be counted as an alternating subarray? 
    # Actually, looking at the problem name "Alternating 'ab'", it implies the pattern ab, ab, ab...
    # Or ba, ba, ba...
    # A single character doesn't really "alternate".
    # Let me re-examine: if max_len is 1, should we return 0 or 1?
    # Sample 2: malayalam -> output 0. There are no 'a' or 'b' pairs that alternate.
    # Wait, 'a' appears in malayalam. m-a-l-a-y-a-l-a-m.
    # The 'a's are separated by other characters, so no contiguous subarray of alternating a/b exists.
    # So if we only have single 'a's or 'b's without alternation, the answer would be 0.
    # But what about a string like "ab"? That's length 2.
    # What about "a"? Should it be 0 or 1?
    
    # Let's reconsider: an alternating subarray of 'ab' means s[i] == 'a' and s[i+1] == 'b' or s[i] == 'b' and s[i+1] == 'a', and this pattern continues.
    # A single character doesn't exhibit alternation.
    # So we should only count lengths >= 2? Or maybe the problem considers length 1 as valid?
    
    # Let's look at the accepted rate and problem statement more carefully.
    # "Largest Alternating 'ab' Subarray" - the 'ab' in quotes suggests the two-character pattern.
    
    # Let me adjust: only count if we have at least 2 characters in the alternating sequence.
    # Actually, let's just track the longest alternating substring consisting of a's and b's.
    # If the result is 1, it means there's a single 'a' or 'b' but no alternation. 
    # Should we return 0 in that case? 
    
    # Hmm, but what if the expected answer for "a" is 1? I'm not sure.
    # Let's think about it differently: the longest substring where every consecutive pair alternates between a and b.
    # For a string of length 1, there are no consecutive pairs, so it vacuously satisfies the condition.
    # But typically in such problems, "alternating" implies at least 2 characters.
    
    # Let's go with the approach: find longest contiguous substring of a's and b's where adjacent chars differ.
    # If the max length found is 0 or 1, but we did find 'a' or 'b', maybe the answer is 0.
    # Actually, for "ab" the answer should be 2. For "aba" the answer is 3. For "a" the answer should be... let's say 0.
    
    # Let me re-examine: perhaps the problem wants the length of the longest substring consisting only of 'a' and 'b' that alternates.
    # I'll return max_len if max_len >= 2, else 0.
    
    if max_len < 2:
        print(0)
    else:
        print(max_len)

if __name__ == "__main__":
    main()
