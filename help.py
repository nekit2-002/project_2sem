# 0 1 1 2 3 5 8 13 21 3fnckmeeejie
def foo(pos):
    if pos < 2:
        return pos
    else:
        return foo(pos - 1) + foo(pos - 2)


print(foo(int(input("Введите число -> "))))
