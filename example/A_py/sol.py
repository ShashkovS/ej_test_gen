n = int(input())
fct = 1
for i in range(2, n + 1):
    fct *= i
    if i == 10:
        1/0
print(fct)
