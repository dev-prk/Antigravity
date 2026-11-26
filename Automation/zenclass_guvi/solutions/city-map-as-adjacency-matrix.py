import sys

def main():
    data = sys.stdin.read().strip().split('\n')
    idx = 0
    n = int(data[idx])
    idx += 1
    
    cities = []
    for _ in range(n):
        cities.append(data[idx].strip())
        idx += 1
    
    city_to_idx = {city: i for i, city in enumerate(cities)}
    
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 1
    
    num_links = int(data[idx])
    idx += 1
    
    for _ in range(num_links):
        parts = data[idx].strip().split()
        idx += 1
        city1, city2 = parts[0], parts[1]
        i1 = city_to_idx[city1]
        i2 = city_to_idx[city2]
        matrix[i1][i2] = 1
        matrix[i2][i1] = 1
    
    header = ' ' + ' '.join(cities)
    print(header)
    
    for city in cities:
        row = city + ' ' + ' '.join(map(str, matrix[city_to_idx[city]]))
        print(row)

if __name__ == "__main__":
    main()
