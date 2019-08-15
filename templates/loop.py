from time import sleep
for i in range(200):
    
    if i % 4 == 0:
        print(i, "special action")
    else:
        print(i)
    sleep(1)
