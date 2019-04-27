import csv
import sys

path = sys.argv[1]
from_row = int(sys.argv[2])
to_row = from_row + int(sys.argv[3])

train_name = 'train_image_x_y_selectedID.csv' 
val_name = 'val_image_x_y_selectedID.csv' 
test_name = 'test_x_y_selectedID.csv' 

with open(str(path)) as f:
    with open(train_name, newline="\n", mode='w+') as out: 
        for n, line in enumerate(f):
            if n <= from_row: 
                out.write(line)
                
with open(str(path)) as f:
    with open(val_name, newline="\n", mode='w+') as out: 
        for n, line in enumerate(f):
            if n >= from_row and n <= to_row: 
                out.write(line)

with open(str(path)) as f:
    with open(test_name, newline="\n", mode='w+') as out: 
        for n, line in enumerate(f):
            if n >= to_row: 
                out.write(line)