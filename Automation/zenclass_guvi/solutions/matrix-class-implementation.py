import sys

class Matrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
    
    def print_rows(self):
        print(self.rows)
    
    def print_cols(self):
        print(self.cols)
    
    def print_elements(self, elements=None):
        if elements is None:
            return
        for row in elements:
            print(' '.join(map(str, row)))

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        print('invalid')
        return
    
    first_line = data[0]
    try:
        rows_str, cols_str = first_line.split('x')
        rows = int(rows_str)
        cols = int(cols_str)
        total_elements = int(data[1])
    except:
        print('invalid')
        return
    
    if rows <= 0 or cols <= 0 or total_elements <= 0:
        print('invalid')
        return
    
    expected_elements = rows * cols
    if total_elements != expected_elements:
        print('invalid')
        return
    
    if len(data[2:]) != total_elements:
        print('invalid')
        return
    
    try:
        elements = list(map(int, data[2:2+total_elements]))
    except:
        print('invalid')
        return
    
    matrix_elements = []
    for i in range(rows):
        row = elements[i*cols:(i+1)*cols]
        matrix_elements.append(row)
    
    m = Matrix(rows, cols)
    m.print_rows()
    m.print_cols()
    m.print_elements(matrix_elements)

if __name__ == "__main__":
    main()
