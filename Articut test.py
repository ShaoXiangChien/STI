from ArticutAPI import Articut
from pprint import pprint

articut = Articut(username="yishin@gmail.com",
                  apikey="UGqaeo46Aw+4HI#q2^P-pAbz!yPXxx6")

sentence="殺人事件今年已發生兩起。"

# result_lv3 = articut.parse(sentence, level="lv3")
result_lv2=articut.parse(sentence, level="lv2")
print(result_lv2)
