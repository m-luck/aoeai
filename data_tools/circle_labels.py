import cv2
import sys

with open(sys.argv[1], 'r') as r:
    for i, line in enumerate(r):
        example_img_path, x, y, selected = line.split(',')
        batch, file_name = example_img_path.split('/')[1:3]
        after_s = file_name.split('-')[1]
        number = file_name.split('.')[0]
        example_ground = (int(x),int(y))
        img = cv2.imread(example_img_path)
        cv2.circle(img, example_ground, 10, (200,100,5), thickness=4, lineType=8, shift=0)
        cv2.imwrite( "label_{0}_{1}.jpg".format(batch,number), img )