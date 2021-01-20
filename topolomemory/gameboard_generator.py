import cv2

img = cv2.imread('../image/1/e.png')
board = cv2.imread('../image/board.png') # 1500 * 1500

# resize
height = img.shape[0]
width = img.shape[1]

img_size = 300
img2 = cv2.resize(img, (img_size, img_size))

# merge
start_width = 270
start_height = 210

board[start_height:start_height + img_size, start_width:start_width + img_size] = img2

cv2.imshow('test', board)
# cv2.imshow('test', img2)

cv2.waitKey(0)