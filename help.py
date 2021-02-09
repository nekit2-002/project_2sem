# 0 1 1 2 3 5 8 13 21
def foo(pos):
    if pos < 2:
        return pos
    else:
        return foo(pos - 1) + foo(pos - 2)

print(foo(8))
