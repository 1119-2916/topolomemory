from game_master import GameMaster
import os
import cv2

img_dir = '../image'
gm = GameMaster(os.path.join(img_dir, 'board.png'))
gm.load_image(img_dir)

str = "1A"

ret = (int(str[0])-1) * 4

for i in range(0, len(str)):
    print(str[i] - 'A')

