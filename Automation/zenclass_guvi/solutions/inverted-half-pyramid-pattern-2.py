import sys

def print_inverted_half_pyramid(R):
    for i in range(R, 0, -1):
        if i == R:
            # First row (full row)
            print(''.join(str(j) for j in range(1, R + 1)))
        elif i == 1:
            # Last row (single digit)
            print('1')
        else:
            # Hollow part
            # First row starts with '1', last element is 'i'
            # Spacing between them: (i - 2) numbers to skip
            middle = i - 2
            if middle == 0:
                # Special case when i = 2: print "1" then skip one, then print "2" but we need "12"
                print("12")
            else:
                # Calculate spaces needed
                # We need to print '1' then some spaces, then 'i'
                # The count of numbers between 1 and i is (i - 1), but we only print 1 and i
                # So we need to show the gap properly
                # Looking at pattern: "1 4" for i=4 means spaces between '1' and '4'
                # Pattern shows: position 0: '1', position 1: ' ', position 2: ' ', position 3: '4'
                # For i=4: we want "1  4" (two spaces)
                # For i=3: we want "1 3" (one space)
                # The formula should be: print '1' + ' '*(i-2) + str(i)
                print('1' + ' ' * (i - 2) + str(i))

if __name__ == "__main__":
    R = int(sys.stdin.readline().strip())
    print_inverted_half_pyramid(R)
