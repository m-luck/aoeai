import random
import sys

with open(sys.argv[1], 'r') as r, open(sys.argv[2], 'w+') as w:
    rows = r.readlines()
    random.shuffle(rows)
    rows = '\n'.join([row.strip() for row in rows])
    w.write(rows)