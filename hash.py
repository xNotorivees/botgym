from functools import reduce
bin(reduce(lambda x, y: 256*x+y, (ord(c) for c in 'hello'), 0))