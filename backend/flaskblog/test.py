items = {'1', '2', '3', '4', '5', '6', '7'}


for item in items:
    if int(item) == 1 or int(item) % 3 == 0:
        print(f'different div {item} endiv')
    else:

        print(f'normal div {item} endiv')