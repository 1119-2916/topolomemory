import os
import cv2
import random
from collections import defaultdict
from card import Card


class GameMaster:
    start_width = 270
    start_height = 210
    card_size = 300
    card_distance = 10
    board_size = 1500

    def __init__(self, board_path):
        self.card_list = []
        self.game_board = cv2.resize(cv2.imread(board_path), (self.board_size, self.board_size))
        self.cards_on_board = []
        self.user_list = []
        self.used_card_set = set()
        self.user_score = defaultdict(int)

    def echo(self, str):
        return str

    def game_reset(self):
        self.user_list = []
        self.used_card_set = set()
        self.user_score = defaultdict(int)

    # path は画像が入っているディレクトリの相対パスを要求
    def load_image(self, path):
        files = os.listdir(path)
        files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]

        for dir in files_dir:
            images = os.listdir(os.path.join(path, dir))

            for image in images:
                img = cv2.imread(os.path.join(path, dir, image))
                img2 = cv2.resize(img, (self.card_size, self.card_size))
                self.card_list.append(Card(img2, dir))

    def card_play(self, index):
        if len(self.cards_on_board) == 16:
            print('error in card_play : fill the board')
            return

        if len(self.card_list) <= index:
            print('error in card_play : IndexOutOfRange')
            return

        if index in self.used_card_set:
            print('warning in card_play : used_card play')
            return

        self.cards_on_board.append(self.card_list[index])
        self.used_card_set.add(index)

    def random_card_play(self):
        index = random.randint(0, len(self.card_list)-1)
        self.card_play(index)

    def generate_gameboard(self):
        cnum = len(self.cards_on_board)
        csize = self.card_size
        ret_image = self.game_board.copy()

        for i in range(0, cnum):
            height = self.start_height + (i // 4) * (csize + self.card_distance)
            width = self.start_width + (i % 4) * (csize + self.card_distance)
            ret_image[height:height + csize, width:width + csize] = self.card_list[i].image

        return ret_image
        # return cv2.imencode('.png', ret_image)

    def erase_card(self, index):
        if len(self.card_list) <= index:
            print('error in erase : out of range')
            return

        self.card_list.pop(index)

    def erase_card_pair(self, index1, index2):
        if len(self.card_list) <= index1:
            print('error in erase : arg1 out of range')
            return

        if len(self.card_list) <= index2:
            print('error in erase : arg2 out of range')
            return

        if index1 < index2:
            self.card_list.pop(index2)
            self.card_list.pop(index1)
        else:
            self.card_list.pop(index1)
            self.card_list.pop(index2)

    def check_card_set(self, index1, index2):
        if len(self.card_list) <= index1:
            print('error in pick_card_set: index1 out of bounds')
            return False

        if len(self.card_list) <= index2:
            print('error in pick_card_set: index2 out of bounds')
            return False

        if index1 == index2:
            print('error in pick_card_set: index1 == index2')
            return False

        # 成功か失敗を返す
        return self.card_list[index1].word == self.card_list[index2].word

    def user_update(self, userID, score):
        self.user_score[userID] += score
