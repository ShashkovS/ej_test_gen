n = int(input())
fct = 1
for i in range(2, n + 1):
    fct *= i
print(fct)
ln = 0
while fct:
    fct //= 10
    ln += 1
print(ln)
