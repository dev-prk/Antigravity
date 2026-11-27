#include <stdio.h>
#include <string.h>

int main() {
    char s[1000];
    if (fgets(s, sizeof(s), stdin) == NULL) {
        return 0;
    }
    
    // Remove trailing newline
    int len = strlen(s);
    if (len > 0 && s[len-1] == '\n') {
        s[len-1] = '\0';
        len--;
    }
    
    if (len <= 1) {
        printf("%s", s);
        return 0;
    }
    
    // Create pointer-based approach
    char result[1000];
    int left = 0, right = len - 1;
    int k = 0;
    int turn = 0; // 0 = take from left (first char to end), 1 = take from right (last char to start)
    
    // Build result by alternating: take first char, move it to end (skip it)
    // So we take chars at positions: 0, 2, 4... from original, then 1, 3, 5... from remaining
    // Or: take from front (even indices), then from front (odd indices)
    // Actually: alternating move first to end, last to start
    // For "abcdef": a bcdef -> bcdefa, then last is a, move to start: abcdef... wait that's wrong
    // Let me re-read: "alternate between moving the first character to the end and the last character to the start"
    // "abcdef": move first (a) to end -> "bcdefa", move last (a) to start -> "abcdef" (back to start!)
    // Hmm that's circular. Let me look at expected: "bdfeca"
    // Original: a b c d e f
    // After reordering to "bdfeca"
    // So it takes odd positions (1-indexed): b, d, f, then e, c, a
    // That's: positions 1,3,5,4,2,0 (0-indexed)
    // Pattern: take from middle-out or specific interleaving...
    
    // Looking at "bdfeca": b(1), d(3), f(5), e(4), c(2), a(0)
    // It's taking: odd indices first, then even indices in reverse
    // Or: take from front half (odd positions), then back half (even positions reversed)
    
    // Actually simpler pattern: 
    // Take characters at odd positions: b,d,f -> "bdf"
    // Take characters at even positions in reverse: a,c,e -> "eca"
    // Result: "bdfeca"
    
    int mid = (len + 1) / 2;
    for (int i = 1; i < len; i += 2) {
        result[k++] = s[i];
    }
    for (int i = (len % 2 == 0) ? len - 2 : len - 1; i >= 0; i -= 2) {
        result[k++] = s[i];
    }
    
    result[k] = '\0';
    printf("%s", result);
    
    return 0;
}
