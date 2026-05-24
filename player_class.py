import random
from data_related import msg_in, robot_random_sleep
from UI import tile_front, tile_back
class Player:
    def __init__(self, Pn: str, name: str = '', avatar: str = '', score: int = 0, dealer_flag = False,
                 tiles = None, missing_suit = 'Not chosen',
                 current_draw: str = None, current_discard: str = None,
                 ):
        self.name = name
        self.Pn = Pn
        self.avatar = avatar
        self.score = score
        self.dealer_flag = dealer_flag
        self.tiles = tiles or { # in python, if an attribute's value of a class is by default list or dict, the value will be shared by all instances!
            'hand': {
                'W': [],
                'T': [],
                'B': []
            },
            'exposed_kong': [],
            'concealed_kong': [],
            'triplet': []
        }
        self.missing_suit = missing_suit
        self.current_draw = current_draw
        self.current_discard = current_discard
    
    def avatar_and_name(self):
        return self.avatar + self.name
    def tiles_sort(self):
        for suit in self.tiles['hand']:
            self.tiles['hand'][suit].sort()
        self.tiles['exposed_kong'].sort()
        self.tiles['concealed_kong'].sort()
        self.tiles['triplet'].sort()
    def get_all_hand_tiles(self):
        return self.tiles['hand']['W'] + self.tiles['hand']['T'] + self.tiles['hand']['B']
    def draw_tile(self, tile: str):
        self.current_draw = tile
    def add_hand(self):
        self.tiles['hand'][self.current_draw[1]].append(self.current_draw)
        self.tiles_sort()
        self.current_draw = None
    def discard_draw(self):
        self.current_discard = self.current_draw
        msg_in(self, f'Discard the tile {tile_front[self.current_discard]} just drawn.')
        self.current_draw = None
    def discard_hand(self, tile):
        self.tiles['hand'][tile[1]].remove(tile)
        self.current_discard = tile
        msg_in(self, f'Discard the tile {tile_front[self.current_discard]}.')
    def exposed_kong(self, kong_list):
        '''
        Move 4 same tiles from hand/current_draw
        into exposed kong area
        '''
        self.tiles['exposed_kong'] += kong_list
        self.tiles['exposed_kong'].sort()
        tile_emoji = tile_front[kong_list[0]]
        msg_in(self, f"Kong! {(tile_emoji + ' ') * 4}")
        if kong_list[0] == self.current_draw:
            self.current_draw = None
        while kong_list[0] in self.tiles['hand'][kong_list[0][1]]:
            self.tiles['hand'][kong_list[0][1]].remove(kong_list[0])
        while kong_list[0] in self.tiles['triplet']:
            self.tiles['triplet'].remove(kong_list[0])
        self.tiles_sort()

    def concealed_kong(self, kong_list):
        '''
        Move 3 same tiles from hand along with captured tile
        into concealed kong area
        '''
        self.tiles['concealed_kong'] += kong_list
        self.tiles['concealed_kong'].sort()
        msg_in(self, f"Kong! {(tile_back + ' ') * 4}")
        if kong_list[0] == self.current_draw:
            self.current_draw = None
        while kong_list[0] in self.tiles['hand'][kong_list[0][1]]:
            self.tiles['hand'][kong_list[0][1]].remove(kong_list[0])
        self.tiles_sort()

    def triplet(self, triplet_list):
        '''
        Move 2 same tiles from hand along with captured tile
        into triplet area
        '''
        self.tiles['triplet'] += triplet_list
        self.tiles['triplet'].sort()
        tile_emoji = tile_front[triplet_list[0]]
        msg_in(self, f"Triplet! {(tile_emoji + ' ') * 3}")
        for i in range(0, 2):
            self.tiles['hand'][triplet_list[0][1]].remove(triplet_list[0])
        self.tiles_sort()


    def __str__(self):
        return self.name
    def after_round_reset(self):
        '''reset everything except for score'''
        self.tiles = {
            'hand': {
                'W': [],
                'T': [],
                'B': []
            },
            'exposed_kong': [],
            'concealed_kong': [],
            'triplet': []
        }
        self.dealer_flag = False
        self.missing_suit = 'Not chosen'
        self.current_draw = None
        self.current_discard = None

# msg_list[i][0]: sender
# msg_list[i][1]: timestamp
# msg_list[i][2]: message content
class Human(Player):
    def prompt_avatar_and_name(self, avatar_list, robot_name_list):
        # name
        while True:
            name = input('Please enter player name(1-10 characters): ').strip()
            if len(name) == 0 or len(name) > 10:
                print('Invalid input, 1-10 characters please.')
                continue
            else:
                self.name = name.title()
                if self.name in robot_name_list:
                    robot_name_list.remove(self.name)
                print(f'Hello, {self.name}!')
                msg_in(self, f"{self.name} joined the game.")
                break
        # avatar
        while True:
            prompt = 'Choose an avatar No. from -\n'
            for i in range(0, len(avatar_list)):
                if ((i + 1) % 5 != 0 or i + 1 == len(avatar_list)) and i != len(avatar_list) - 1:
                    prompt += str(i + 1) + ': ' + avatar_list[i] + '    '
                else:
                    prompt += str(i + 1) + ': ' + avatar_list[i] + '    \n'
            select = input(prompt).strip()

            if (select.isdigit() and 1 <= int(select) <= len(avatar_list)):
                self.avatar = avatar_list.pop(int(select) - 1)
                print(f'Awesome, {self.avatar} looks amazing!')
                msg_in(self, f"{self.name} chose {self.avatar} as their avatar!")
                break
            else:
                print('Invalid input, please enter a valid avatar number.')
                continue
    def add_hand_or_discard(self):
        '''
        Return:
        False - discard current_draw
        True - add current_draw into hand
        '''
        while True:
            try_input = input(
                f'You drew {tile_front[self.current_draw]}. Do you want to add it to your hand? (1: yes / 2: no) '
            )
            if try_input.strip().lower() in ['y', 'yes', 'yeah', 'ya', '1', 'positive']:
                self.add_hand()
                return True
            elif try_input.strip().lower() in ['n', 'no', 'nah', '2', 'negative']:
                self.discard_draw()
                return False
            else:
                print('Invalid input. Please try again - ')

    def mahjong_or_not(self):
        while True:
            try_input = input('You have a chance to mahjong, do you wanna do it? (1: yes / 2: no)')
            if try_input.strip().lower() in ['y', 'yes', 'yeah', 'ya', '1', 'positive']:
                return True
            elif try_input.strip().lower() in ['n', 'no', 'nah', '2', 'negative']:
                return False
            else:
                print('Invalid input. Please try again - ')
    def kong_or_not(self, possible_kong_list):
        '''
        Return:
        False - give up kong chance
        list  - selected kong tile list
        '''
        if not possible_kong_list or len(possible_kong_list) % 4 != 0:
            return False
        while True:
            prompt = 'You have a chance to kong:\n'
            for i in range(0, len(possible_kong_list), 4):
                prompt += (str(i // 4 + 1)+ ': ' # choice No.
                    + tile_front[possible_kong_list[i]]+ ' '
                    + tile_front[possible_kong_list[i + 1]]+ ' '
                    + tile_front[possible_kong_list[i + 2]]+ ' '
                    + tile_front[possible_kong_list[i + 3]]+ '\n'
                )
            prompt += '0: give up this chance\n'
            prompt += 'Please enter your choice: '
            try_input = input(prompt).strip()
            if try_input.isdigit():
                try_input = int(try_input)
                if try_input == 0:
                    return False
                elif 1 <= try_input <= len(possible_kong_list) // 4: # when valid input
                    return possible_kong_list[(try_input - 1) * 4 : try_input * 4]
            else:
                print('Invalid input. Please try again - ')
    def triplet_or_not(self, possible_triplet_list):
        '''
        Return:
        False - give up triplet chance
        list  - selected triplet tile list
        '''
        if not possible_triplet_list or len(possible_triplet_list) != 3:
            return False      
        prompt = f'You have a chance to triplet: {tile_front[possible_triplet_list[0]]} {tile_front[possible_triplet_list[1]]} {tile_front[possible_triplet_list[2]]}, do you wanna do it? (1: yes / 2: no) '
        while True:
            try_input = input(prompt)
            if try_input.strip().lower() in ['y', 'yes', 'yeah', 'ya', '1', 'positive']:
                return possible_triplet_list
            elif try_input.strip().lower() in ['n', 'no', 'nah', '2', 'negative']:
                return False
            else:
                print('Invalid input. Please try again - ')

    def discard(self):
        '''
        Return:
        tile - selected discarded tile
        '''
        while True:
            self.tiles_sort()
            hand_tiles = self.get_all_hand_tiles()
            prompt = 'Choose a tile to discard:\n'
            for i, t in enumerate(hand_tiles):
                prompt += str(i + 1) + ':' + tile_front[t] + '    '
                if (i + 1) % 10 == 0:
                    prompt += '\n'
            prompt += '\nPlease enter your choice: '
            try_input = input(prompt).strip()
            if try_input.isdigit():
                try_input = int(try_input)
                if 1 <= try_input <= len(hand_tiles):
                    chosen_tile = hand_tiles[try_input - 1]
                    self.discard_hand(chosen_tile)
                    return chosen_tile
            print('Invalid input. Please try again - ')
        
    def agree_to_new_round(self):
        while True:
            try_input = input("Such a fun game, isn't it? Do you wanna start a new round? (1: yes / 2: no) ")
            if try_input.strip().lower() in ['y', 'yes', 'yeah', 'ya', '1', 'positive']:
                return True
            elif try_input.strip().lower() in ['n', 'no', 'nah', '2', 'negative']:
                return False
            else:
                print('Invalid input. Please try again - ')
    def define_missing_suit(self):
        while True:
            try_input = input("Choose your missing suit: 1. Wan/Characters  2. Tiao/Bamboo  3. Bing/Dots ")
            if try_input.strip().lower() in ['characters', 'character', 'wan', 'w', 'c', '1']:
                self.missing_suit = 'W'
                break
            elif try_input.strip().lower() in ['tiao', 'bamboo', 'b', 't', '2']:
                self.missing_suit = 'T'
                break
            elif try_input.strip().lower() in ['bing', 'dot', 'dots', 'd', '3']:
                self.missing_suit = 'B'
                break
            else:
                print('Invalid input. Please try again - ')

class Robot(Player):
    def prompt_avatar_and_name(self, avatar_list, robot_name_list):
        robot_random_sleep()
        self.name = random.choice(robot_name_list)
        robot_name_list.remove(self.name)
        msg_in(self, f"{self.name} joined the game.")
        robot_random_sleep()
        if self.name == 'Stewie':
            self.avatar = '🥟'
            if self.avatar in avatar_list:
                avatar_list.remove(self.avatar)
        elif self.name == 'Brian':
            self.avatar = '🐶'
            if self.avatar in avatar_list:
                avatar_list.remove(self.avatar)
        else:
            self.avatar = random.choice(avatar_list)
            avatar_list.remove(self.avatar)
        msg_in(self, f"{self.name} chose {self.avatar} as their avatar!")
    
    def add_hand_or_discard(self):
        robot_random_sleep()
        '''
        Return:
        False - discard current_draw
        True - add current_draw into hand

        Robot discard logic:
        1. If the drawn tile is the missing suit:
        directly discard it
        2. Otherwise:
        compare all tiles in hand and current draw
        3. Tile score rules:
        single tile = -1 point
        single tile not connected to nearby tiles = -1 point
        isolated tile with no same-suit tiles within +/-3 = -2 points
        pair = +1 point
        triplet = +3 points
        4. Lower score tiles are more likely to be discarded
        5. If scores are the same:
        discard priority:
        1/9 > 2/8 > 3/7 > 4/6 > 5
        6. If priority is still the same:
        randomly choose one
        7. Avoid discarding:
        tiles that can form kong
        tiles that can upgrade existing triplets into kong
        '''
        if self.current_draw is None:
            return False
        if self.current_draw[1] == self.missing_suit:
            self.discard_draw()
            return False
        
        def tile_priority(tile):
            num = int(tile[0])
            if num in [1, 9]:
                return 0
            elif num in [2, 8]:
                return 1
            elif num in [3, 7]:
                return 2
            elif num in [4, 6]:
                return 3
            else:
                return 4

        def tile_score(tile, other_tiles):
            same_count = other_tiles.count(tile)
            if same_count >= 3:
                return None

            score = 0
            if same_count == 0:
                score -= 1
                num = int(tile[0])
                suit = tile[1]
                connected = False
                for n in [num - 1, num + 1]:
                    if 1 <= n <= 9 and f'{n}{suit}' in other_tiles:
                        connected = True
                        break
                if not connected:
                    score -= 1
                    nearby = False
                    for n in [num - 3, num - 2, num + 2, num + 3]:
                        if 1 <= n <= 9 and f'{n}{suit}' in other_tiles:
                            nearby = True
                            break
                    if not nearby:
                        score -= 2
            elif same_count == 1:
                score += 1
            elif same_count == 2:
                score += 3
            return score

        hand_tiles = self.get_all_hand_tiles()
        all_tiles = hand_tiles + [self.current_draw]
        all_tiles.sort()

        protected_tiles = set()
        if all_tiles.count(self.current_draw) >= 4:
            protected_tiles.add(self.current_draw)
        if self.tiles['triplet'].count(self.current_draw) >= 3:
            protected_tiles.add(self.current_draw)

        candidate_list = []
        for tile in all_tiles:
            if tile in protected_tiles:
                continue
            remaining = all_tiles.copy()
            remaining.remove(tile)
            score = tile_score(tile, remaining)
            if score is None:
                continue
            candidate_list.append((score, tile_priority(tile), random.random(), tile))

        if len(candidate_list) == 0:
            self.add_hand()
            self.tiles_sort()
            return True

        candidate_list.sort()
        chosen_tile = candidate_list[0][3]

        if chosen_tile == self.current_draw:
            self.discard_draw()
            return False
        else:
            self.add_hand()
            self.tiles_sort()
            return True

    def discard(self):
        robot_random_sleep()
        '''
        Return:
        tile - selected discarded tile

        Robot discard logic:
        1. Check all hand tiles
        2. If there are still tiles from missing suit:
        randomly discard one of them
        3. Otherwise:
        calculate score for every tile
        4. Tile score rules:
        single tile = -1 point
        single tile not connected to nearby tiles = -1 point
        isolated tile with no same-suit tiles within +/-3 = -2 points
        pair = +1 point
        triplet = +3 points
        four same tiles = +6 points
        5. Discard the tile with the lowest score
        6. If scores are the same:
        discard priority:
        1/9 > 2/8 > 3/7 > 4/6 > 5
        7. If priority is still the same:
        randomly choose one
        '''
        hand_tiles = self.get_all_hand_tiles()
        if not hand_tiles:
            return None

        missing_tiles = [t for t in hand_tiles if t[1] == self.missing_suit]
        if len(missing_tiles) > 0:
            chosen_tile = random.choice(missing_tiles)
            self.discard_hand(chosen_tile)
            return chosen_tile

        def tile_priority(tile):
            num = int(tile[0])
            if num in [1, 9]:
                return 0
            elif num in [2, 8]:
                return 1
            elif num in [3, 7]:
                return 2
            elif num in [4, 6]:
                return 3
            else:
                return 4

        def tile_score(tile, tiles):
            same_count = tiles.count(tile)
            score = 0
            if same_count == 0:
                score -= 1
                num = int(tile[0])
                suit = tile[1]
                connected = False
                for n in [num - 1, num + 1]:
                    if 1 <= n <= 9 and f'{n}{suit}' in tiles:
                        connected = True
                        break
                if not connected:
                    score -= 1
                    nearby = False
                    for n in [num - 3, num - 2, num + 2, num + 3]:
                        if 1 <= n <= 9 and f'{n}{suit}' in tiles:
                            nearby = True
                            break
                    if not nearby:
                        score -= 2
            elif same_count == 1:
                score += 1
            elif same_count == 2:
                score += 3
            elif same_count >= 3:
                score += 6
            return score

        candidate_list = []
        for tile in hand_tiles:
            remaining = hand_tiles.copy()
            remaining.remove(tile)
            score = tile_score(tile, remaining)
            candidate_list.append((score, tile_priority(tile), tile))

        min_score = min(item[0] for item in candidate_list)
        score_candidate = [item for item in candidate_list if item[0] == min_score]

        min_priority = min(item[1] for item in score_candidate)
        priority_candidate = [item for item in score_candidate if item[1] == min_priority]

        chosen_tile = random.choice(priority_candidate)[2]
        self.discard_hand(chosen_tile)
        return chosen_tile

    def mahjong_or_not(self):
        robot_random_sleep()
        return True
    def kong_or_not(self, possible_kong_list):
        robot_random_sleep()
        '''
        Return:
        False - no kong chance
        list  - selected kong tiles
        '''
        if not possible_kong_list or len(possible_kong_list) % 4 != 0:
            return False
        return possible_kong_list[0:4]
    def triplet_or_not(self, possible_triplet_list):
        robot_random_sleep()
        '''
        Return:
        False - no triplet chance
        list  - selected triplet tile list
        '''
        if not possible_triplet_list or len(possible_triplet_list) != 3:
            return False
        return possible_triplet_list
    
    def define_missing_suit(self):
        robot_random_sleep()
        '''
        1. Choose the suit with the smallest amount of tiles first
        2. If multiple suits have the same amount: compare suit scores
        2.1 Repeated tiles score:
            pair = 2 points
            triplet = 4 points
            four identical tiles = 8 points
        2.2 Tile range score:
            max - min <= 2 : +4 points
            max - min == 3 : +2 points
            max - min == 4 : +1 point
        3. Choose the suit with the lowest score as missing suit
        4. If scores are still tied:
            randomly choose one
        '''
        suit_count = {}
        suit_score = {}
        for suit in ['W', 'T', 'B']:
            tiles = self.tiles['hand'][suit].copy()
            if self.current_draw and self.current_draw[1] == suit:
                tiles.append(self.current_draw)
            suit_count[suit] = len(tiles)
            score = 0
            counter = {}
            for t in tiles:
                num = int(t[0])
                if num not in counter:
                    counter[num] = 0
                counter[num] += 1
            for num in counter:
                if counter[num] == 2:
                    score += 2
                elif counter[num] == 3:
                    score += 4
                elif counter[num] >= 4:
                    score += 8
            if len(tiles) > 0:
                nums = []
                for t in tiles:
                    nums.append(int(t[0]))
                diff = max(nums) - min(nums)
                if diff <= 2:
                    score += 4
                elif diff == 3:
                    score += 2
                elif diff == 4:
                    score += 1
            suit_score[suit] = score

        min_count = min(suit_count.values())
        count_candidate = []
        for suit in suit_count:
            if suit_count[suit] == min_count:
                count_candidate.append(suit)

        min_score = min(suit_score[suit] for suit in count_candidate)
        score_candidate = []
        for suit in count_candidate:
            if suit_score[suit] == min_score:
                score_candidate.append(suit)

        self.missing_suit = random.choice(score_candidate)
