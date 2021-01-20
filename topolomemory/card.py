

class Card:

    def __init__(self, image, word):
        self.image = image # 画像
        self.word = word  # 画像のかるた的な要素の判別

    def is_topology(self, other):
        return self.word == other.word
