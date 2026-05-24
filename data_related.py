import random
from datetime import datetime
import time


# initialise tile_wall, 108 tiles in total
def new_tile_wall():
    tile_wall = []
    for i in range(1,10):
        for s in ['W','T','B']:
            for n in range(0,4):
                tile_wall.append(str(i)+s)
    random.shuffle(tile_wall)
    return tile_wall
# tile_dic = {
#     "1W": 4, "2W": 4, "3W": 4, "4W": 4, "5W": 4, "6W": 4, "7W": 4, "8W": 4, "9W": 4,
#     "1T": 4, "2T": 4, "3T": 4, "4T": 4, "5T": 4, "6T": 4, "7T": 4, "8T": 4, "9T": 4,
#     "1B": 4, "2B": 4, "3B": 4, "4B": 4, "5B": 4, "6B": 4, "7B": 4, "8B": 4, "9B": 4,
# }

scoreboard = {
    "P1" : 0,
    "P2" : 0,
    "P3" : 0,
    "P4" : 0
}

avatar_list = [
    "👽", "😎", "🐱", "🥳", "🥬",
    "🤠", "🧙", "🦸", "🦊", "🐼",
    "🐯", "👼", "🍎", "🍵", "🥟",
    "🎲", "🀄", "🐶", "🔥", "⭐",
    "🐲", "🫄", "☠️"
]

# msg_list[i][0]: sender (Pn)
# msg_list[i][1]: timestamp
# msg_list[i][2]: message content
msg_list = [] 
def msg_in(sender, message_content:str):
    msg_list.append([sender, datetime.now().strftime("%H:%M:%S"), message_content])
def recent_msg(msg_list):
    print('Recent events:')
    for i in msg_list[-12:]:
        print(f'[{i[1]}][{i[0].avatar_and_name()}] {i[2]}')
        

### player 
robot_name_list = [
    'Louis', 'Peter', 'Stewie', 'Brian', 'Meg', 'Chris'
] 

def robot_random_sleep():
    time.sleep(random.randint(0, 1))
