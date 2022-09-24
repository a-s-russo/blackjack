# Blackjack card game inspired by project #4 from the book
# 'The Big Book of Small Python Projects' by Al Sweigart

import random
import sys


class Player:
    def __init__(self, name, target=21, stop_at=None, money=0, state_cards=False):
        self.name = name
        self.money = money
        self.score = 0
        self.hand = []
        self.is_bust = False
        self.bet = 0
        self.continue_playing = True
        self.first_deal = True
        self.stop_at = stop_at
        self.state_cards = state_cards
        self.target = target

    def add_card_to_hand(self, card):
        self.hand.append(card)
        self.score_hand()

    def score_hand(self):
        score = 0
        num_aces = 0
        for card in self.hand:
            rank = card[1:]
            if rank in ['J', 'Q', 'K']:
                score += 10
            elif rank == 'A':
                score += 1
                num_aces += 1
            else:
                score += int(rank)
        for ace in range(num_aces):
            if score + 10 <= self.target:
                score += 10
        self.score = score

    def reset_player(self):
        self.hand = []
        self.bet = 0
        self.is_bust = False
        self.continue_playing = True
        self.first_deal = True
        self.score = 0


class BlackJack:
    def __init__(self, target=21, money=5000):
        self.player = Player('Player', target=target, money=money, state_cards=True)
        self.dealer = Player('Dealer', target=target, stop_at=17)
        self.deck = []
        self.game_continues = True
        self.target = target

    def print_intro(self):
        print('''
Rules:
    Try to get as close to 21 without going over.
    Kings, Queens, and Jacks are worth 10 points.
    Aces are worth 1 or 11 points.
    Cards 2 through 10 are worth their face value.
    (H)it to take another card.
    (S)tand to stop taking cards.
    On your first play, you can (D)ouble down to increase your bet
    but must hit exactly one more time before standing.
    In case of a tie, the bet is returned to the player.
    The dealer stops hitting at 17.\n''')

    def reset_deck(self):
        self.deck = [
            'CA', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'CJ', 'CQ', 'CK',
            'DA', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'DJ', 'DQ', 'DK',
            'HA', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK',
            'SA', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'SJ', 'SQ', 'SK',
        ]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_card(self, player):
        card = self.deck.pop()
        player.add_card_to_hand(card)
        return card

    def get_bet(self, player, max_bet=None):
        print('Money: ${:,}'.format(player.money))
        max_bet = max_bet or player.money
        valid_inputs = [str(num) for num in range(1, max_bet + 1)]
        bet = input("How much do you bet? $(1-{:,})\n".format(max_bet))
        while bet not in valid_inputs:
            print('That is not a valid entry. Please try again:')
            bet = input("How much do you bet? $(1-{:,})\n".format(max_bet))
        else:
            player.bet = int(bet)
        return print('Bet: ${:,}'.format(player.bet), end='\n\n')

    def get_action(self, player):
        actions = {'H': '(H)it', 'S': '(S)tand'}
        if player.first_deal and player.bet != player.money:
            actions['D'] = '(D)ouble down'
            player.first_deal = False
        print(', '.join(actions.values()))
        action = input().upper()
        while action not in actions.keys():
            action = input('That is not a valid entry. Please try again:').upper()
        return action

    def hit(self, player):
        if player.stop_at is None or player.score < player.stop_at:
            card = self.draw_card(player)
            if player.score > self.target:
                player.is_bust = True
            if player.state_cards:
                self.state_card_drawn(card)
        if (player.stop_at and player.score >= player.stop_at) or player.is_bust:
            player.continue_playing = False

    def stand(self, player):
        player.continue_playing = False

    def double_down(self, player):
        previous_bet = player.bet
        self.get_bet(player, max_bet=player.money - player.bet)
        player.bet += previous_bet
        print("Bet increased to: ${:,}".format(self.player.bet))
        self.hit(player)
        self.stand(player)

    def process_action(self, player):
        action = self.get_action(player)
        if action.upper() == 'H':
            self.hit(player)
        elif action.upper() == 'S':
            self.stand(player)
        else:
            self.double_down(player)

    def finish_dealer(self, dealer, player):
        while dealer.continue_playing and not player.is_bust:
            print('Dealer hits...\n')
            self.hit(dealer)
            if not dealer.is_bust and dealer.score < dealer.stop_at:
                self.print_hand(dealer, reveal=False)
                self.print_hand(self.player)
                _ = input('Press Enter to continue...')
        self.print_hand(dealer)
        self.print_hand(player)

    def determine_outcome(self, dealer, player):
        if not player.is_bust:
            if not dealer.is_bust:
                if player.score == dealer.score:
                    print("It's a tie, and the bet is returned to you.\n")
                elif player.score > dealer.score:
                    print("You won ${:,}!\n".format(player.bet))
                    player.money += player.bet
                else:
                    print("You lost!\n")
                    player.money -= player.bet
            else:
                print("Dealer busts! You win ${:,}!".format(player.bet))
                player.money += player.bet
        else:
            print("You bust!\n")
            player.money -= player.bet

    def get_suit_symbol(self, letter):
        suits = {
            'C': chr(9827),
            'D': chr(9830),
            'H': chr(9829),
            'S': chr(9824)
        }
        return suits[letter]

    def state_card_drawn(self, card):
        rank = card[1:]
        suit = self.get_suit_symbol(card[0])
        print("You drew a {} of {}\n".format(rank, suit))

    def print_hand(self, player, reveal=True):
        score = str(player.score) if reveal else '???'
        print(player.name.upper(), score, sep=": ", end='\n\n')
        lines = ['', '', '', '']
        for card in player.hand:
            rank = card[1:]
            suit = self.get_suit_symbol(card[0])
            lines[0] += '|{}{}| '.format(rank.ljust(2, chr(8254)), chr(8254))
            lines[1] += '| {} | '.format(suit)
            lines[2] += '|_{}| '.format(rank.rjust(2, '_'))
        if not reveal:
            lines[0] = lines[0][0] + '##' + lines[0][3:]
            lines[1] = lines[1][0] + '###' + lines[1][4:]
            lines[2] = lines[2][0:2] + '##' + lines[2][4:]
        for line in lines:
            print(line)

    def continue_game(self, dealer, player):
        print('\n\nMoney: ${:,}'.format(player.money), end='\n')
        if player.money == 0:
            print('You have no more money.\n\n')
            self.game_continues = False
        else:
            response = input("Continue playing? (y/n)\n")
            if response.upper() in ['Y', 'YES']:
                player.reset_player()
                dealer.reset_player()
            else:
                self.game_continues = False

    def game(self):
        self.print_intro()
        while self.game_continues:
            self.reset_deck()
            self.shuffle_deck()
            self.get_bet(self.player)
            self.draw_card(self.player)
            self.draw_card(self.dealer)
            self.draw_card(self.player)
            self.draw_card(self.dealer)
            self.print_hand(self.dealer, reveal=False)
            self.print_hand(self.player)
            while self.player.continue_playing:
                self.process_action(self.player)
                self.print_hand(self.dealer, reveal=False)
                self.print_hand(self.player)
            self.finish_dealer(self.dealer, self.player)
            self.determine_outcome(self.dealer, self.player)
            self.continue_game(self.dealer, self.player)
        sys.exit()


bj = BlackJack()
bj.game()
