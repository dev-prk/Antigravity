def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n, series=None):
    if series is None:
        series = []
    if len(series) == n:
        return series
    if len(series) == 0:
        series.append(0)
    elif len(series) == 1:
        series.append(1)
    else:
        series.append(series[-1] + series[-2])
    return fibonacci(n, series)

n = int(input())
fact = factorial(n)
fib_series = fibonacci(n)
print(fact)
print(fib_series)
