import math
import time


t1 = time.process_time()


def do(a, b):
    c = 4*a + math.sqrt(b/2)
    print(c)

a = int(input("Please enter value a: "))
b = int(input("Please enter value b: "))


do(a, b)
time.sleep(1)
print(t1)

