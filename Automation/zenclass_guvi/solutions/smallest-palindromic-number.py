def next_palindrome():
    n = int(input().strip())
    digits = list(map(int, input().split()))
    
    original_num = ''.join(map(str, digits))
    original = int(original_num)
    length = len(digits)
    
    def is_palindrome(s):
        return s == s[::-1]
    
    result = original_num
    
    while True:
        if is_palindrome(result):
            if int(result) > original:
                return result
        
        result_list = list(result)
        i = length - 1
        while i >= 0:
            if result_list[i] < '9':
                result_list[i] = str(int(result_list[i]) + 1)
                for j in range(i + 1, length):
                    result_list[j] = '0'
                break
            i -= 1
        result = ''.join(result_list)
        
        if len(result) > length:
            result = '1' + '0' * (length - 1) + '1'

print(next_palindrome())
