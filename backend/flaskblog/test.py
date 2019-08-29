lis = (1, 2, 3, 4, 5, 6)

for x, y in zip(*[iter(lis)]*2):
    print(x, y)