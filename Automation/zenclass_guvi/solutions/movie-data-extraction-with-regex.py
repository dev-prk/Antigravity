import re
import sys

def get_movies(data):
    pattern = r'^([^()]+?)\s*\((\d{4})\)|(?<=\),\s)([^()]+?)\s*\((\d{4})\)'
    matches = re.findall(pattern, data)
    result = []
    for match in matches:
        if match[0]:
            result.append((match[0].strip(), match[1]))
        else:
            result.append((match[2].strip(), match[3]))
    return result

def main():
    data = sys.stdin.read().strip()
    result = get_movies(data)
    print(result)

if __name__ == "__main__":
    main()
