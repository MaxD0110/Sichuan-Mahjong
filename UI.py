from data_related import recent_msg

tile_front = {
    "1W": "🀇", "2W": "🀈", "3W": "🀉", "4W": "🀊", "5W": "🀋", "6W": "🀌", "7W": "🀍", "8W": "🀎", "9W": "🀏",
    "1T": "🀐", "2T": "🀑", "3T": "🀒", "4T": "🀓", "5T": "🀔", "6T": "🀕", "7T": "🀖", "8T": "🀗", "9T": "🀘",
    "1B": "🀙", "2B": "🀚", "3B": "🀛", "4B": "🀜", "5B": "🀝", "6B": "🀞", "7B": "🀟", "8B": "🀠", "9B": "🀡",
}

tile_back = '🀫'

def print_scoreboard(P_list):
    print(f'Scoreboard: {P_list[0].avatar_and_name()}:{str(P_list[0].score)}  {P_list[1].avatar_and_name()}:{str(P_list[1].score)}  {P_list[2].avatar_and_name()}:{str(P_list[2].score)}  {P_list[3].avatar_and_name()}:{str(P_list[3].score)}')

def in_round_UI(round, tiles_wall_amount, viewer_P, current_P, P_list, msg_list):
    '''
    UI dispay when each turn begins or new msg is sent.
    '''
    print('Sichuan Mahjong - Console Edition')
    print('========================================================================')
    print(f'Turn: {current_P.avatar_and_name()}     |    Round: {round}   |   Wall tiles: {tiles_wall_amount}')
    print('------------------------------------------------------------------------')
    print_scoreboard(P_list)
    print('========================================================================')
    for P in P_list:
        P.tiles_sort()
        s = P.avatar_and_name()
        if P.dealer_flag:
            s += ' [Dealer]'
        if P == viewer_P:
            s += ' [You]'
        print(s)

        print(f'   Score: {P.score}    Missing suit: {P.missing_suit}')

        hand_tiles_image = ''
        for t in P.get_all_hand_tiles():
            if P == viewer_P:
                hand_tiles_image += (tile_front[t] + ' ')
            else:
                hand_tiles_image += (tile_back + ' ')

        if P == viewer_P and P.current_draw:
            recently_draw_image = tile_front[P.current_draw]
        elif P != viewer_P and P.current_draw:
            recently_draw_image = tile_back
        else:
            recently_draw_image = 'Empty'
        print(f"    Hand ({len(P.get_all_hand_tiles())} tiles): {hand_tiles_image}")

        current_draw_image = tile_front[P.current_draw] if P.current_draw else 'Empty'
        current_discard_image = tile_front[P.current_discard] if P.current_discard else 'Empty'
        if P == viewer_P:
            print(f'    Recently draw: {current_draw_image}    Current discard: {current_discard_image}')
        else:
            print(f'    Current discard: {current_discard_image}')
        
        triplet_image = ''
        for t in P.tiles['triplet']:
            triplet_image += (tile_front[t] + ' ')
        exposed_kong_image = ''
        for t in P.tiles['exposed_kong']:
            exposed_kong_image += (tile_front[t] + ' ')
        concealed_kong_image = ''
        for t in P.tiles['concealed_kong']:
            if viewer_P == P:
                concealed_kong_image += (tile_front[t] + ' ')
            else:
                concealed_kong_image += (tile_back + ' ')
        print(f'    Triplet: {triplet_image}')
        print(f'    Concealed Kong: {concealed_kong_image}   Exposed Kong: {exposed_kong_image}')
        print('------------------------------------------------------------------------')
    recent_msg(msg_list)
    print('\n\n\n')

def round_end_results(round, winner, P_list):
    print('------------------------------------------------------------------------')
    if winner:
        print(f'Round {str(round)} ended, {winner.avatar_and_name()} is the winner, congrats!')
    else:
        print(f"Round {str(round)} ended, it's a tie.")
    print('------------------------------------------------------------------------')
    print_scoreboard(P_list)
    print('------------------------------------------------------------------------')
