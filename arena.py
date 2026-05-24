### This is the entrance of the program ###

from data_related import avatar_list, robot_name_list, msg_list, msg_in, recent_msg, new_tile_wall
from player_class import Player, Human, Robot
from UI import in_round_UI, print_scoreboard, round_end_results,tile_front
import random
import os


def prompt_rules():
    try_input = input('New to Mahjong, or just pretending🤪? Want to read the rules first? (1: yes / 2: no) ')
    if try_input.strip().lower() in ['y', 'yes', 'yeah', 'ya', '1', 'positive']:
        print('------------------------------------------------------------------------')
        rules_path = os.path.join(os.path.dirname(__file__), 'mahjong_rules.txt') # cwd to arena.py's dir
        rules_file = open(rules_path, 'r')
        print(rules_file.read())
        rules_file.close()
        print('------------------------------------------------------------------------')
        input('Rules closed. Press Enter to start the game!')


def game_loop():
    # initialization
    round_count = 0
    print('Sichuan Mahjong - Console Edition')
    print('========================================================================')
    prompt_rules()
    P1 = Human(Pn = 'P1')
    P2 = Robot(Pn = 'P2')
    P3 = Robot(Pn = 'P3')
    P4 = Robot(Pn = 'P4')
    player_list = [P1, P2, P3, P4]

    for p in player_list:
        p.prompt_avatar_and_name(avatar_list, robot_name_list)

    dealer_index = random.randint(0, 3) 
    player_list[dealer_index].dealer_flag = True
    player_list_dealer_first = [player_list[dealer_index - 4], player_list[dealer_index - 3], player_list[dealer_index - 2],player_list[dealer_index - 1]]
    print('------------------------------------------------------------------------')
    recent_msg(msg_list)

    while True:
        round_count += 1
        # msg_in(player_list[dealer_index], f"Round {str(round_count)} started. Say hi to dealer: {player_list[dealer_index].avatar_and_name()}.")
        print(f"Round {str(round_count)} started. Say hi to dealer: {player_list[dealer_index].avatar_and_name()}.")
        tile_wall = new_tile_wall()
        # distribute tiles
        for P in player_list_dealer_first:
            tile_d = 14 if P.dealer_flag else 13
            for i in range(0, tile_d):
                pop_out = tile_wall.pop(0)
                if pop_out[1] == 'W':
                    P.tiles['hand']['W'].append(pop_out)
                elif pop_out[1] == 'T':
                    P.tiles['hand']['T'].append(pop_out)
                elif pop_out[1] == 'B':
                    P.tiles['hand']['B'].append(pop_out)
            in_round_UI(round_count, len(tile_wall), P1, P, player_list_dealer_first, msg_list)
        for P in player_list_dealer_first:
            P.define_missing_suit()

        # rounds
        round_end = False
        dealer_first_turn = True
        recently_kong_player = None
        recently_triplet_player = None
        winner = None
        while not round_end:
            for P in player_list_dealer_first:
                # turn_begin_clean_up
                P.current_draw = None
                P.current_discard = None

                # move to recently konged or tripleted player's turn and reset kong flag (since triplet flag still needed to skip draw the tile)
                if recently_kong_player:
                    if P != recently_kong_player:
                        continue
                    recently_kong_player = None
                elif recently_triplet_player:
                    if P != recently_triplet_player:
                        continue

                P.tiles_sort()
                player_list_current_P_first = [player_list[player_list.index(P) - 4], player_list[player_list.index(P) - 3], player_list[player_list.index(P) - 2], player_list[player_list.index(P) - 1]]

                # turn begin 
                if not recently_triplet_player or recently_triplet_player != P:
                    if dealer_first_turn and P == player_list_dealer_first[0]:
                        dealer_first_turn = False
                    else:
                        # draw a tile 
                        # tie 
                        if len(tile_wall) == 0:
                            msg_in(P, 'Oops, there is no tile left in the wall. Tie!')
                            round_end = True
                            break
                        P.draw_tile(tile_wall.pop())
                        in_round_UI(round_count, len(tile_wall), P1, P, player_list_dealer_first, msg_list)
                        
                        # add to hand or discard
                        discard_flag = not P.add_hand_or_discard()
                        in_round_UI(round_count, len(tile_wall), P1, P, player_list_dealer_first, msg_list)
                        #after discard other players' act 
                        if discard_flag:
                            round_end, winner = after_discard_mahjong_check(player_list_current_P_first, P1, P.current_discard, round_count, tile_wall, player_list_dealer_first, msg_list)
                            if round_end:
                                break
                            recently_kong_player, recently_triplet_player = after_discard_kong_triplet_check(player_list_current_P_first, P1, P.current_discard, round_count, tile_wall, player_list_dealer_first, msg_list)
                            if recently_kong_player or recently_triplet_player:
                                continue
                            continue
                                    
                else:
                    recently_triplet_player = None
                    
                # turn begin (self_draw) mahjong check
                if mahjong_check(P.get_all_hand_tiles(), P.missing_suit):
                    if P.mahjong_or_not():
                        after_mahjong(P.get_all_hand_tiles(), round_count, tile_wall, P1, P, player_list_dealer_first, msg_list)
                        winner = P
                        round_end = True
                        break

                # turn begin added kong check
                possible_kong_list =  added_kong_check(P.get_all_hand_tiles(), P.tiles['triplet'], P.missing_suit)
                while possible_kong_list:
                    player_kong_choice = P.kong_or_not(possible_kong_list) # false or selected kong tiles
                    # if player chose to kong
                    if player_kong_choice:
                        for t in player_kong_choice:
                            possible_kong_list.remove(t)
                        P.exposed_kong(player_kong_choice)
                        if len(tile_wall) == 0:
                            msg_in(P, 'Oops, there is no tile left in the wall. Tie!')
                            round_end = True
                            break
                        P.draw_tile(tile_wall.pop())
                        P.add_hand()
                        in_round_UI(round_count, len(tile_wall), P1, P, player_list_dealer_first, msg_list)
                    else:
                        break
                if round_end:
                    break

                # turn begin concealed kong check
                possible_kong_list =  concealed_kong_check(P.get_all_hand_tiles(), P.missing_suit)
                while possible_kong_list:
                    player_kong_choice = P.kong_or_not(possible_kong_list) # false or selected kong tiles
                    # if player chose to kong
                    if player_kong_choice:
                        for t in player_kong_choice:
                            possible_kong_list.remove(t)
                        P.concealed_kong(player_kong_choice)
                        if len(tile_wall) == 0:
                            msg_in(P, 'Oops, there is no tile left in the wall. Tie!')
                            round_end = True
                            break
                        P.draw_tile(tile_wall.pop())
                        P.add_hand()
                        in_round_UI(round_count, len(tile_wall), P1, P, player_list_dealer_first, msg_list)
                    else:
                        break
                if round_end:
                    break
                    
                # discard
                    #for 
                        # mahjong check 
                        # kong check
                        # triplet check
                tile_current_P_discard = P.discard()
                in_round_UI(round_count, len(tile_wall), P1, P, player_list_dealer_first, msg_list)
                round_end, winner = after_discard_mahjong_check(player_list_current_P_first, P1, P.current_discard, round_count, tile_wall, player_list_dealer_first, msg_list)
                if round_end:
                    break
                recently_kong_player, recently_triplet_player = after_discard_kong_triplet_check(player_list_current_P_first, P1, P.current_discard, round_count, tile_wall, player_list_dealer_first, msg_list)
                if recently_kong_player or recently_triplet_player:
                    continue
                
    
        # round_end results
        round_end_results(round_count, winner, player_list)

        agree_new_round = P1.agree_to_new_round()
        if round_end and agree_new_round:
            #clean the table
            for P in player_list:
                P.after_round_reset()
            recently_kong_player = None
            recently_triplet_player = None
            #next dealer  
            dealer_index = (dealer_index + 1) % 4
            player_list[dealer_index].dealer_flag = True
            player_list_dealer_first = [player_list[dealer_index - 4], player_list[dealer_index - 3], player_list[dealer_index - 2],player_list[dealer_index - 1]]
            continue
        
        if round_end and not agree_new_round:
            #clean the table
            for P in player_list:
                P.after_round_reset()
            print_scoreboard(player_list)
            break
    
def after_discard_mahjong_check(player_list_current_P_first, view_P, tile_current_P_discard, round_count, tile_wall, player_list_dealer_first, msg_list):
    '''
    when each player discards a tile, others determine whether to mahjong
    return : (round_end_flag, winner if exist otherwise None)
    '''
    if not tile_current_P_discard:
        return False, None
    for Pi in player_list_current_P_first[1:]:
        if mahjong_check(Pi.get_all_hand_tiles() + [tile_current_P_discard], Pi.missing_suit):
            if Pi.mahjong_or_not():
                after_mahjong(Pi.get_all_hand_tiles() + [tile_current_P_discard], round_count, tile_wall, view_P, Pi, player_list_dealer_first, msg_list)
                return True, Pi
    return False, None


def after_discard_kong_triplet_check(player_list_current_P_first, view_P, tile_current_P_discard, round_count, tile_wall, player_list_dealer_first, msg_list):
    '''
    when each player discards a tile, after eligible player dicided whether to mahjong,
    everyone except who discards determines whether to kong > triplet
    return : (Player just konged(or None), Player just tripleted(or None))
    '''
    current_kong_P = None
    current_triplet_P = None

    for Pi in player_list_current_P_first[1:]:
        possible_kong_list = exposed_kong_check(Pi.get_all_hand_tiles() + Pi.tiles['triplet'], tile_current_P_discard, Pi.missing_suit)
        if possible_kong_list:
            player_kong_choice = Pi.kong_or_not(possible_kong_list)
            if player_kong_choice:
                Pi.exposed_kong(player_kong_choice)
                in_round_UI(round_count, len(tile_wall), view_P, Pi, player_list_dealer_first, msg_list)
                current_kong_P = Pi
                return current_kong_P, current_triplet_P

        possible_triplet_list = triplet_check(Pi.get_all_hand_tiles(), tile_current_P_discard, Pi.missing_suit)
        if possible_triplet_list:
            player_triplet_choice = Pi.triplet_or_not(possible_triplet_list)
            if player_triplet_choice:
                Pi.triplet(possible_triplet_list)
                in_round_UI(round_count, len(tile_wall), view_P, Pi, player_list_dealer_first, msg_list)
                current_triplet_P = Pi
                return current_kong_P, current_triplet_P

    return current_kong_P, current_triplet_P

# def after_discard(player_list_current_P_first, view_P, tile_current_P_discard, round_count, tile_wall, player_list_dealer_first, msg_list):
#     '''
#     when each player discards a tile, others determine whether to mahjong > kong > triplet
#     return : (round_end_flag, winner if exist otherwise None, Player just konged(or None), Player just tripleted(or None))
#     '''
#     winner = None
#     current_kong_P = None
#     current_triplet_P = None
#     for Pi in player_list_current_P_first[1: ]:
#         round_end_flag = False
#         #mahjong check
#         if mahjong_check(Pi.get_all_hand_tiles() + [tile_current_P_discard], Pi.missing_suit):
#             if Pi.mahjong_or_not():
#                 after_mahjong(Pi.get_all_hand_tiles() + [tile_current_P_discard], round_count, tile_wall, view_P, Pi, player_list_dealer_first, msg_list)
#                 round_end_flag = True
#                 winner = Pi
#                 break
#         #exposed kong check
#         possible_kong_list = exposed_kong_check(Pi.get_all_hand_tiles() + Pi.tiles['triplet'], tile_current_P_discard, Pi.missing_suit)
#         if possible_kong_list:
#             player_kong_choice = Pi.kong_or_not(possible_kong_list) # false or selected kong tiles
#             # if player chose to kong
#             if player_kong_choice:
#                 Pi.exposed_kong(player_kong_choice)
#                 in_round_UI(round_count, len(tile_wall), view_P, Pi, player_list_dealer_first, msg_list)
#                 current_kong_P = Pi
#                 break
#         # triplet check
#         possible_triplet_list = triplet_check(Pi.get_all_hand_tiles(), tile_current_P_discard, Pi.missing_suit)
#         if possible_triplet_list:
#             player_triplet_choice = Pi.triplet_or_not(possible_triplet_list)
#             # if player chose to triplet
#             if player_triplet_choice:
#                 Pi.triplet(possible_triplet_list)
#                 in_round_UI(round_count, len(tile_wall), view_P, Pi, player_list_dealer_first, msg_list)
#                 current_triplet_P = Pi
#                 break

#     return round_end_flag, winner, current_kong_P, current_triplet_P

        
def concealed_kong_check(tiles, missing_suit):
    '''receive tile list, return possible kong list (except missing suit tiles)'''
    possible_kong_list = []
    for suit in ['W', 'T', 'B']:
        if suit == missing_suit:
            continue
        for i in range(1, 10):
            tile = str(i) + suit
            if tiles.count(tile) == 4:
                for n in range(0, 4):
                    possible_kong_list.append(tile)
    return possible_kong_list

def added_kong_check(tiles, triplet_tiles, missing_suit):
    '''receive hand tiles and triplet tiles,
    return possible added kong list (except missing suit tiles)'''
    possible_kong_list = []
    for t in triplet_tiles:
        if t[1] == missing_suit:
            continue
        if tiles.count(t) >= 1 and t not in possible_kong_list:
            for n in range(0, 4):
                possible_kong_list.append(t)
    return possible_kong_list

def triplet_check(tiles, new_tile, missing_suit):
    '''receive hand tiles + new tile, 
    return possible triplet list (except missing suit tiles) or []'''
    possible_triplet_list = []
    if not new_tile:
        return possible_triplet_list
    if new_tile[1] == missing_suit:
        return possible_triplet_list
    if tiles.count(new_tile) == 2:
        for n in range(0, 3):
            possible_triplet_list.append(new_tile)
    return possible_triplet_list   

def exposed_kong_check(tiles, new_tile, missing_suit):
    '''receive hand tiles (including existing triplet tiles) + new tile, 
    return possible exposed kong list (except missing suit tiles)'''
    possible_kong_list = []
    if not new_tile:
        return possible_kong_list
    if new_tile[1] == missing_suit:
        return possible_kong_list
    if tiles.count(new_tile) >= 3:
        for n in range(0, 4):
            possible_kong_list.append(new_tile)
    return possible_kong_list

def mahjong_check(tiles, missing_suit, pair_select = False):
    # check missing suit
    for t in tiles:
        if t[1] == missing_suit:
            return False
    
    # recursion start
    if len(tiles) == 0:
        return pair_select
    tiles = sorted(tiles)
    tile_selected = tiles[0] # chose a random tile to start

    # try to find and remove pairs
    if not pair_select and tiles.count(tile_selected) >= 2:
        remaining = tiles.copy()
        remaining.remove(tile_selected)
        remaining.remove(tile_selected)
        if mahjong_check(remaining, missing_suit, True):
            return True

    # try to find and remove triplets
    if tiles.count(tile_selected) >= 3:
        remaining = tiles.copy()
        remaining.remove(tile_selected)
        remaining.remove(tile_selected)
        remaining.remove(tile_selected)
        if mahjong_check(remaining, missing_suit, pair_select):
            return True

    # try to find and remove sequences
    num = int(tile_selected[0])
    suit = tile_selected[1]
    second = f'{num+1}{suit}'
    third = f'{num+2}{suit}'
    if second in tiles and third in tiles:
        remaining = tiles.copy()
        remaining.remove(tile_selected)
        remaining.remove(second)
        remaining.remove(third)
        if mahjong_check(remaining, missing_suit, pair_select):
            return True

    return False

def after_mahjong(mahjong_tile_list, round_count, tile_wall, view_P, current_P, player_list, msg_list):
    mahjong_tile = ''
    for t in mahjong_tile_list:
        mahjong_tile += tile_front[t]
    msg = f'Mahjong! {current_P.name} win the round! Their mahjong is {mahjong_tile}' 
    msg_in(current_P, msg)
    current_P.score += 3
    for P in player_list:
        if P != current_P:
            P.score -= 1
    in_round_UI(round_count, len(tile_wall), view_P, current_P, player_list, msg_list)

def start_game():
    print('\n' * 100)
    game_loop()

if __name__ == '__main__':
    start_game()
