import tkinter as tk
from tkinter import messagebox
import numpy as np
import gym
from gym import spaces

class BlackJackEnv(gym.Env):

    metadata = {'render.modes':['human']}

    def __init__(self):
        self.observation_space = spaces.Discrete(2000000)
        self.action_space = spaces.Discrete(4)
        self.step_count = 0                        ### Number of actions taken in the game till now
        self.double_count1 = 0
        self.double_count2 = 0
        self.stick_happened = False
        self.can_split = 0
        self.done_split = 0
        self.stage = 1
        self.actions = ['hit', 'stick', 'double_down', 'split']


    def check_usable_ace(self,hand):
        ### Creating a temporary hand taking the Ace's value as 11 to check of usability
        temp_hand = hand.copy()

        ### Checking if the hand has any ace, if not then returns False
        if np.any(temp_hand == 1):
            ### If the hand has any ace then replace the ace(1) with 11 in the temporary hand,
            ### if there are more than one ace then replaces the first ace(1) with 11

            temp_hand[np.where(temp_hand == 1)[0][0]] = 11

            ### After replacement if sum is less than equal to 21, then the ace is usable
            if temp_hand.sum() <= 21:
                return True

        return False

    def use_ace(self,hand):
        temp_hand = hand.copy()
        temp_hand[np.where(temp_hand == 1)[0][0]] = 11
        return temp_hand


    def reset(self):
        self.double_count1 = 0
        self.double_count2 = 0
        self.can_split = 0
        self.done_split = 0
        self.stage = 1
        self.stick_happened = False
        distr = [1/13] * 9 + [4/13]
        ### New Player Hand
        self.current_hand1 = np.random.choice(range(1, 11), 2, p=distr)
        self.current_hand2 = np.zeros(1, dtype=int)
        if self.current_hand1[0] == self.current_hand1[1]:
          self.can_split = 1

        ### Initialising Usable Ace as False

        self.usable_ace1 = False
        self.usable_ace2 = False

        ### Variable is used to inform whether the dealer has sticked,
        ### Used to know when to terminate the game

        self.dealer_stick = False


        ### Checking if player hand has Usable Ace, if yes, then replacing it with 11.
        if self.check_usable_ace(self.current_hand1):
            self.usable_ace1 = True
            self.current_hand1 = self.use_ace(self.current_hand1)

        ### State variable Current Sum
        self.current_sum1 = self.current_hand1.sum()
        self.current_sum2 = 0

        ### Dealer's New Hand
        self.dealer_hand = np.random.choice(range(1, 11), 2, p=distr)

        ### Dealer's Sum
        self.dealer_sum = self.dealer_hand.sum()

        ### State Variable: Dealer Showing Card
        self.dealer_showing_card = self.dealer_hand[0]

        ### Checking if Dealer's hand has Usable Ace, if yes, then replacing it with 11.
        if self.check_usable_ace(self.dealer_hand):
            temp_dealer_hand = self.use_ace(self.dealer_hand)
            self.dealer_sum = temp_dealer_hand.sum()


    def take_turn(self,player,hand,number):

        if player == 'dealer':
            distr = [1/13] * 9 + [4/13]
            ### takes a new random card
            new_card = np.random.choice(range(1, 11), p=distr)

            ### adding new card to the players hand and making a temporary new hand
            new_dealer_hand = np.array(hand.tolist() +  [new_card])

            ### Check if there is usable ace
            if self.check_usable_ace(new_dealer_hand):

                ### replace ace(1) with 11
                new_dealer_hand = self.use_ace(new_dealer_hand)

            ### Assigning the temporary hand to the players actual hand
            self.dealer_hand = new_dealer_hand

            ### Updating the players hand sum variable
            self.dealer_sum = self.dealer_hand.sum()

        if player == 'player':
            distr = [1/13] * 9 + [4/13]
            ### takes a new random card
            new_card = np.random.choice(range(1, 11), p=distr)

            ### adding new card to the players hand and making a temporary new hand
            new_player_hand = np.array(hand.tolist()+ [new_card])

            ### Check if there is usable ace
            if self.check_usable_ace(new_player_hand):

                ### replace ace(1) with 11
                self.usable_ace = True
                new_player_hand = self.use_ace(new_player_hand)

            if number == 1:
              self.current_hand1 = new_player_hand
              self.current_sum1 = self.current_hand1.sum()
            elif number == 2:
            ### Assigning the temporary hand to the players actual hand
              self.current_hand2 = new_player_hand
              ### Updating the players hand sum variable
              self.current_sum2 = self.current_hand2.sum()



    def check_game_status(self, dd1 = 0, dd2 = 0, mode = 'final'):

        result = {'winner':'',
                 'is_done1': False,
                 'is_done2': False,
                 'reward':0}

        if mode == 'check':

          if self.current_sum1 >= 21:
            result['is_done1'] = True

          if self.current_sum2 >= 21:
            result['is_done2'] = True

        elif mode == 'final':
          if self.done_split == 0 and self.stage == 3:
            dupla = 0
            if dd1 == 0:
              dupla = 1
            else:
              dupla = 2 * dd1

            if self.current_sum1 > 21 and self.dealer_sum == 21 or self.dealer_sum == 21 and self.current_sum1 < 21 or self.dealer_sum < 21 and self.current_sum1 > 21:
                  result['winner'] = 'dealer'
                  result['is_done1'] = True
                  result['is_done2'] = True
                  result['reward'] = -1 * dupla
            elif self.current_sum1 == 21 and self.dealer_sum > 21 or self.dealer_sum < 21 and self.current_sum1 == 21 or self.dealer_sum > 21 and self.current_sum1 < 21:
                  result['winner'] = 'player'
                  result['is_done1'] = True
                  result['is_done2'] = True
                  result['reward'] = 1 * dupla

            elif self.current_sum1 == 21 and self.dealer_sum == 21 or self.dealer_sum > 21 and self.current_sum1 > 21:
                  result['winner'] = 'draw'
                  result['is_done1'] = True
                  result['is_done2'] = True
                  result['reward'] = 0

            else:
              result['is_done1'] = True
              result['is_done2'] = True
              diff_21_player = 21 - self.current_sum1
              diff_21_dealer = 21 - self.dealer_sum

              if diff_21_player > diff_21_dealer:
                  result['reward'] = -1 * dupla
                  result['winner'] = 'dealer'
              elif diff_21_player < diff_21_dealer:
                  result['reward'] = 1 * dupla
                  result['winner'] = 'player'
              else:
                  result['reward'] = 0
                  result['winner'] = 'draw'

              return result

            return result

          elif self.done_split == 1 and self.stage == 3:
            dupla1 = 0
            dupla2 = 0
            if dd1 == 0:
              dupla1 = 1
            else:
              dupla1 = 2 * dd1
            if dd2 == 0:
              dupla2 = 1
            else:
              dupla2 = 2 * dd2

            #if mode == 'normal':
            if self.current_sum1 == 21 and self.current_sum2 == 21 and self.dealer_sum == 21 or self.current_sum1 > 21 and self.current_sum2 > 21 and self.dealer_sum > 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 0
                result['winner'] = 'draw'
                return result

            elif self.dealer_sum > 21 and self.current_sum1 <= 21 and self.current_sum2 <= 21 or self.current_sum1 == 21 and self.current_sum2 == 21 and self.dealer_sum < 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 1 * dupla1 + 1 * dupla2
                result['winner'] = 'player'
                return result

            elif self.dealer_sum == 21 and self.current_sum1 < 21 and self.current_sum2 < 21 or self.dealer_sum <= 21 and self.current_sum1 > 21 and self.current_sum2 > 21 or self.dealer_sum == 21 and self.current_sum1 < 21 and self.current_sum2 > 21 or self.dealer_sum == 21 and self.current_sum1 > 21 and self.current_sum2 < 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = -1 * dupla1 -1 * dupla2
                result['winner'] = 'dealer'
                return result

            elif self.dealer_sum == 21 and self.current_sum1 < 21 and self.current_sum2 == 21 or self.dealer_sum == 21 and self.current_sum1 > 21 and self.current_sum2 == 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = -1 * dupla1
                result['winner'] = 'dealer'
                return result

            elif self.dealer_sum == 21 and self.current_sum1 == 21 and self.current_sum2 < 21 or self.dealer_sum == 21 and self.current_sum1 == 21 and self.current_sum2 > 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = -1 * dupla2
                result['winner'] = 'dealer'
                return result

            elif self.dealer_sum > 21 and self.current_sum1 < 21 and self.current_sum2 > 21 or self.dealer_sum > 21 and self.current_sum1 == 21 and self.current_sum2 > 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 1 * dupla1
                result['winner'] = 'player'
                return result

            elif self.dealer_sum > 21 and self.current_sum1 > 21 and self.current_sum2 < 21 or self.dealer_sum > 21 and self.current_sum1 > 21 and self.current_sum2 == 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 1 * dupla2
                result['winner'] = 'player'
                return result

            elif self.dealer_sum < 21 and self.current_sum1 == 21 and self.current_sum2 > 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 1 * dupla1 - 1 * dupla2
                if 1 * dupla1 - 1 * dupla2 > 0:
                    result['winner'] = 'player'
                elif 1 * dupla1 - 1 * dupla2 == 0:
                    result['winner'] = 'draw'
                else:
                    result['winner'] = 'dealer'
                return result

            elif self.dealer_sum < 21 and self.current_sum1 > 21 and self.current_sum2 == 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = -1 * dupla1 + 1 * dupla2
                if -1 * dupla1 + 1 * dupla2 > 0:
                    result['winner'] = 'player'
                elif -1 * dupla1 + 1 * dupla2 == 0:
                    result['winner'] = 'draw'
                else:
                    result['winner'] = 'dealer'
                return result

            elif self.dealer_sum < 21 and self.current_sum1 > 21 and self.current_sum2 < 21:
                result['is_done1'] = True
                result['is_done2'] = True
                if self.current_sum2 - self.dealer_sum > 0:
                    result['reward'] = -1 * dupla1 + 1 * dupla2
                    if -1 * dupla1 + 1 * dupla2 > 0:
                        result['winner'] = 'player'
                    elif -1 * dupla1 + 1 * dupla2 == 0:
                        result['winner'] = 'draw'
                    else:
                        result['winner'] = 'dealer'
                elif self.current_sum2 - self.dealer_sum == 0:
                    result['winner'] = 'dealer'
                    result['reward'] = -1 * dupla1
                else:
                    result['winner'] = 'dealer'
                    result['reward'] = -1 * dupla1 - 1 * dupla2
                return result

            elif self.dealer_sum < 21 and self.current_sum1 < 21 and self.current_sum2 > 21:
                result['is_done1'] = True
                result['is_done2'] = True
                if self.current_sum1 - self.dealer_sum > 0:
                    result['reward'] = 1 * dupla1 - 1 * dupla2
                    if 1 * dupla1 - 1 * dupla2 > 0:
                        result['winner'] = 'player'
                    elif 1 * dupla1 - 1 * dupla2 == 0:
                        result['winner'] = 'draw'
                    else:
                        result['winner'] = 'dealer'
                elif self.current_sum1 - self.dealer_sum == 0:
                    result['winner'] = 'dealer'
                    result['reward'] = -1 * dupla2
                else:
                    result['winner'] = 'dealer'
                    result['reward'] = -1 * dupla1 - 1 * dupla2
                return result

            elif self.dealer_sum < 21 and self.current_sum1 < 21 and self.current_sum2 == 21:
                result['is_done1'] = True
                result['is_done2'] = True
                if self.current_sum1 - self.dealer_sum > 0:
                    result['reward'] = 1 * dupla1 + 1 * dupla2
                    result['winner'] = 'player'
                elif self.current_sum1 - self.dealer_sum == 0:
                    result['winner'] = 'player'
                    result['reward'] = 1 * dupla2
                else:
                    result['reward'] = -1 * dupla1 + 1 * dupla2
                    if -1 * dupla1 + 1 * dupla2 > 0:
                        result['winner'] = 'player'
                    elif -1 * dupla1 + 1 * dupla2 == 0:
                        result['winner'] = 'draw'
                    else:
                        result['winner'] = 'dealer'
                return result

            elif self.dealer_sum < 21 and self.current_sum1 == 21 and self.current_sum2 < 21:
                result['is_done1'] = True
                result['is_done2'] = True
                if self.current_sum2 - self.dealer_sum > 0:
                    result['reward'] = 1 * dupla1 + 1 * dupla2
                    result['winner'] = 'player'
                elif self.current_sum2 - self.dealer_sum == 0:
                    result['winner'] = 'player'
                    result['reward'] = 1 * dupla1
                else:
                    result['reward'] = 1 * dupla1 - 1 * dupla2
                    if 1 * dupla1 - 1 * dupla2 > 0:
                        result['winner'] = 'player'
                    elif 1 * dupla1 - 1 * dupla2 == 0:
                        result['winner'] = 'draw'
                    else:
                        result['winner'] = 'dealer'
                return result

            #elif mode == 'compare':
            else:
                result['is_done1'] = True
                result['is_done2'] = True
                diff_21_player1 = 21 - self.current_sum1
                diff_21_player2 = 21 - self.current_sum2
                diff_21_dealer = 21 - self.dealer_sum

                if diff_21_player1 > diff_21_dealer and diff_21_player2 > diff_21_dealer:
                    result['winner'] = 'dealer'
                    result['reward'] = -1 * dupla1 - 1 * dupla2
                elif diff_21_player1 < diff_21_dealer and diff_21_player2 < diff_21_dealer:
                    result['winner'] = 'player'
                    result['reward'] = 1 * dupla1 + 1 * dupla2
                elif diff_21_player1 < diff_21_dealer and diff_21_player2 > diff_21_dealer:
                    result['reward'] = 1 * dupla1 - 1 * dupla2
                    if 1 * dupla1 - 1 * dupla2 > 0:
                        result['winner'] = 'player'
                    elif 1 * dupla1 - 1 * dupla2 == 0:
                        result['winner'] = 'draw'
                    else:
                        result['winner'] = 'dealer'
                else:
                    result['reward'] = -1 * dupla1 + 1 * dupla2
                    if 1 * dupla1 - 1 * dupla2 > 0:
                        result['winner'] = 'player'
                    elif 1 * dupla1 - 1 * dupla2 == 0:
                        result['winner'] = 'draw'
                    else:
                        result['winner'] = 'dealer'
                return result

        return result

    def step(self,action):

        self.step_count += 1  ### Number of actions taken in the game till now

        result = {'winner':'',
                 'is_done1': False,
                 'is_done2': False,
                 'reward':0}

        ### Before taking the first step of the game we need to check for "natural"
        ### winning condition if the initial two cards of the players are 21
        ### If anyone has 21, then that player wins, if both have 21, then the game is
        ### drawn. Otherwise the game will continue


        if self.stage == 1:

          if self.step_count == 1:
            if self.check_usable_ace(self.current_hand1):
                self.current_hand1 = self.use_ace(self.current_hand1)
            if self.check_usable_ace(self.dealer_hand):
                self.dealer_hand = self.use_ace(self.dealer_hand)

            if self.current_sum1 == 21 and self.dealer_sum == 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 0
                result['winner'] = 'draw'
                return result

            elif self.current_sum1 == 21 and self.dealer_sum < 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = 1
                result['winner'] = 'player'
                return result

            elif self.dealer_sum == 21 and self.current_sum1 < 21:
                result['is_done1'] = True
                result['is_done2'] = True
                result['reward'] = -1
                result['winner'] = 'dealer'
                return result

            if self.dealer_sum >= 17:
                self.dealer_stick = True

          if action == 0:

            if self.done_split == 0:
              ### Player Takes Turn
              self.take_turn('player', self.current_hand1, 1)
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              if result['is_done1'] == True:
                self.stage = 3
                result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
                result['is_done2'] = True
                return result

            else:
              self.take_turn('player', self.current_hand1, 1)
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              if result['is_done1'] == True:
                self.stage = 2
                self.take_turn('player', self.current_hand2, 2)
                return result


          if action == 1:

            if self.done_split == 0:
              if self.stick_happened == False:
                self.stick_happened = True
              if self.dealer_stick == True:
                return self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')

              while self.dealer_sum < 17:
                self.take_turn('dealer', self.dealer_hand, 0)
                #result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              self.dealer_stick = True
              self.stage = 3
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
              return result


            else:
              self.stage = 2
              self.take_turn('player', self.current_hand2, 2)
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              result['is_done1'] = True
              return result

          if action == 2: ### double down

            if self.done_split == 0:
              self.double_count1 = 1
              ### Player Takes Turn
              self.take_turn('player', self.current_hand1, 1)
              if self.dealer_stick == True:  ### if dealer has already sticked
                    return self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
              while self.dealer_sum < 17:
                self.take_turn('dealer', self.dealer_hand, 0)
                #result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              self.stage = 3
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
              return result
            else:
              self.double_count1 = 1
              self.take_turn('player', self.current_hand1, 1)
              self.stage = 2
              self.take_turn('player', self.current_hand2, 2)
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              return result


          if action == 3 and self.can_split == 1 and self.done_split != 1: ### split
            self.can_split = 0
            self.done_split = 1
            elso_elem = np.array([self.current_hand1[0]], dtype=self.current_hand1.dtype)
            masodik_elem = np.array([self.current_hand1[1]], dtype=self.current_hand1.dtype)
            self.current_hand1 = elso_elem
            self.current_hand2 = masodik_elem
            self.take_turn('player', self.current_hand1, 1)
            ### Checking game status
            result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
            return result

        elif self.stage == 2:

          if action == 0:

            self.take_turn('player', self.current_hand2, 2)

            ### Checking game status
            result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
            if result['is_done2'] == True:
                #return result
                while self.dealer_sum < 17:
                    self.take_turn('dealer', self.dealer_hand, 0)
                    #result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
                self.stage = 3
                result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
                #result['is_done1'] = True
                return result



          if action == 1:  ### stick

              if self.stick_happened == False:
                self.stick_happened = True
              ### Dealers Turn
              while self.dealer_sum < 17:
                self.take_turn('dealer', self.dealer_hand, 0)
                #result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              self.stage = 3
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
              result['is_done2'] = True
              return result


          if action == 2: ### double down

              self.double_count2 = 1
              ### Player Takes Turn
              self.take_turn('player', self.current_hand2, 2)

              ### Dealers Turn
              while self.dealer_sum < 17:
                self.take_turn('dealer', self.dealer_hand, 0)
                #result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'check')
              self.stage = 3
              result = self.check_game_status(dd1 = self.double_count1, dd2 = self.double_count2, mode = 'final')
              result['is_done2'] = True
              return result

        return result
    
    def get_current_state(self):
        '''
        returns the current state variables, current_sum, dealer_showing_card, usable_ace
        '''
        current_state = {}

        current_state['current_hand1'] = self.current_hand1
        current_state['current_hand2'] = self.current_hand2
        current_state['current_dealer_hand'] = self.dealer_hand
        current_state['current_dealer_sum'] = self.dealer_sum
        current_state['current_sum1'] = self.current_sum1
        current_state['current_sum2'] = self.current_sum2
        current_state['dealer_showing_card'] = self.dealer_showing_card
        current_state['stage'] = self.stage
        current_state['usable_ace1'] = self.usable_ace1
        current_state['usable_ace2'] = self.usable_ace2
        current_state['stick_happened'] = self.stick_happened
        current_state['double_count1'] = self.double_count1
        current_state['double_count2'] = self.double_count2
        current_state['can_split'] = self.can_split
        current_state['done_split'] = self.done_split

        return current_state
    
    def render(self):

        print('OBSERVABLE STATES')
        print('Current Sum 1 - {}'.format(self.current_sum1))
        print('Current Sum 2 - {}'.format(self.current_sum2))
        print('Dealer Showing Card - {}'.format(self.dealer_showing_card))
        print('Stage - {}'.format(self.stage))
        print('Usable Ace1 - {}'.format(self.usable_ace1))
        print('Usable Ace2 - {}'.format(self.usable_ace2))
        print('Stick happened - {}'.format(self.stick_happened))
        print('Double down 1 - {}'.format(self.double_count1))
        print('Double down 2 - {}'.format(self.double_count2))
        print('Can split - {}'.format(self.can_split))
        print('Done split - {}'.format(self.done_split))

        print('AUXILLARY INFORMATION ------------------------------')
        print('Current Hand 1 - {}'.format(self.current_hand1))
        print('Current Hand 2 - {}'.format(self.current_hand2))
        print('Dealer Hand - {}'.format(self.dealer_hand))
        print('Dealer Sum - {}'.format(self.dealer_sum))

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.env = BlackJackEnv()
        self.root.title("Blackjack Game")
        self.create_widgets()
        self.env.reset()  # Ensure the environment starts fresh
        self.update_display()

    def create_widgets(self):
        self.player_hand_label = tk.Label(self.root, text="Player Hand: ")
        self.player_hand_label.pack()
        self.player_hand2_label = tk.Label(self.root, text="Player Hand 2: ")
        self.player_hand2_label.pack()
        self.dealer_hand_label = tk.Label(self.root, text="Dealer Hand: ")
        self.dealer_hand_label.pack()
        self.actions_frame = tk.Frame(self.root)
        self.actions_frame.pack()
        self.hit_button = tk.Button(self.actions_frame, text="Hit", command=lambda: self.take_action(0))
        self.hit_button.pack(side=tk.LEFT)
        self.stick_button = tk.Button(self.actions_frame, text="Stick", command=lambda: self.take_action(1))
        self.stick_button.pack(side=tk.LEFT)
        self.double_down_button = tk.Button(self.actions_frame, text="Double Down", command=lambda: self.take_action(2))
        self.double_down_button.pack(side=tk.LEFT)
        self.split_button = tk.Button(self.actions_frame, text="Split", command=lambda: self.take_action(3))
        self.split_button.pack(side=tk.LEFT)
        self.reset_button = tk.Button(self.root, text="Reset", command=self.reset_game)
        self.reset_button.pack()
        self.message_label = tk.Label(self.root, text="")
        self.message_label.pack()

    def take_action(self, action):
        result = self.env.step(action)
        self.update_display()
        if result['is_done1'] and result['is_done2']:
            self.show_message(result['winner'], result['reward'])

    def reset_game(self):
        self.env.reset()
        self.update_display()
        self.message_label.config(text="")

    def update_display(self):
        self.player_hand_label.config(text=f" (Player's hand 1: {self.env.get_current_state()['current_hand1']}), (Player's sum 1: {self.env.get_current_state()['current_sum1']})")
        self.player_hand2_label.config(text=f" (Player's hand 2: {self.env.get_current_state()['current_hand2']}), (Player's sum 2: {self.env.get_current_state()['current_sum2']})")
        self.dealer_hand_label.config(text=f" (Dealer's hand: {self.env.get_current_state()['current_dealer_hand']}), (Dealer's sum: {self.env.get_current_state()['current_dealer_sum']})")
        self.split_button.config(state=tk.NORMAL if self.env.can_split and not self.env.done_split else tk.DISABLED)

    def show_message(self, winner, reward):
        self.message_label.config(text=f"Winner: {winner}, Reward: {reward}")


if __name__ == "__main__":
    root = tk.Tk()
    gui = BlackjackGUI(root)
    root.mainloop()
