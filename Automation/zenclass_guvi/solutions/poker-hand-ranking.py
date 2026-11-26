import sys
from collections import Counter

# Card value mapping
VALUE_ORDER = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
               'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

def parse_hand(cards):
    """Parse a list of 5 card strings into a hand representation"""
    values = []
    suits = []
    for card in cards:
        val = card[0]
        suit = card[1]
        values.append(VALUE_ORDER[val])
        suits.append(suit)
    return sorted(values, reverse=True), suits

def is_straight(values):
    """Check if values form a straight"""
    if len(set(values)) != 5:
        return False
    if values[0] - values[4] == 4:
        return True
    # Check for wheel (A-2-3-4-5)
    if values == [14, 5, 4, 3, 2]:
        return True
    return False

def evaluate_hand(hand):
    """Evaluate a hand and return a tuple for comparison"""
    values, suits = hand
    value_counts = Counter(values)
    counts = sorted(value_counts.values(), reverse=True)
    
    # Sort values by frequency then by rank
    value_freq = sorted(value_counts.items(), key=lambda x: (-x[1], -x[0]))
    kickers = [v for v, c in value_freq]
    
    # Check for flush
    is_flush = len(set(suits)) == 1
    
    # Check for straight
    is_strt = is_straight(values)
    
    # Determine hand rank
    if is_flush and is_strt:
        # Straight flush
        if values == [14, 5, 4, 3, 2]:
            return (8, 5)  # Wheel is lowest straight flush
        return (8, values[0])
    
    if counts == [4, 1]:
        # Four of a kind
        return (7, kickers[0], kickers[1])
    
    if counts == [3, 2]:
        # Full house
        return (6, kickers[0], kickers[1])
    
    if is_flush:
        # Flush - return all values as kickers
        return (5, values[0], values[1], values[2], values[3], values[4])
    
    if is_strt:
        # Straight
        if values == [14, 5, 4, 3, 2]:
            return (4, 5)  # Wheel is lowest straight
        return (4, values[0])
    
    if counts == [3, 1, 1]:
        # Three of a kind
        return (3, kickers[0], kickers[1], kickers[2])
    
    if counts == [2, 2, 1]:
        # Two pairs
        return (2, kickers[0], kickers[1], kickers[2])
    
    if counts == [2, 1, 1, 1]:
        # One pair
        return (1, kickers[0], kickers[1], kickers[2], kickers[3])
    
    # High card
    return (0, values[0], values[1], values[2], values[3], values[4])

def compare_hands(black_hand, white_hand):
    """Compare two hands and return result"""
    black_eval = evaluate_hand(black_hand)
    white_eval = evaluate_hand(white_hand)
    
    if black_eval > white_eval:
        return "Black wins"
    elif white_eval > black_eval:
        return "White wins"
    else:
        return "Tie"

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        cards = line.split()
        black_cards = cards[:5]
        white_cards = cards[5:]
        
        black_hand = parse_hand(black_cards)
        white_hand = parse_hand(white_cards)
        
        result = compare_hands(black_hand, white_hand)
        print(result)

if __name__ == "__main__":
    main()
