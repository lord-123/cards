import treys

PLAYER_ACTIVE = 1
PLAYER_FOLDED = 0

class Player:
    def __init__(self, chip_count, name=""):
        self.verbose = verbose
        self.chip_count = chip_count
        self.name = name
        self.hand = []
        self.status = PLAYER_ACTIVE

    # returns amount of money to add to the pot
    def get_action(self, game_state):
        successful = False
        money = 0
        while not successful:
            try:
                print(f"Player {self.name} turn ({treys.Card.ints_to_pretty_str(self.hand)})")
                money = int(input("How much to bet? "))
                successful = True
            except ValueError:
                successful = False
        return money

class Poker:
    def __init__(self, players, big_blind, small_blind, verbose=False):
        self.players = players
        self.big_blind = big_blind
        self.small_blind = small_blind
        self.dealer = 0

    def active_player_count(self):
        return len([p for p in self.players if p.status == PLAYER_ACTIVE])

    def player_n(self, n):
        return n%len(self.players)

    def display_players(self):
        for p in self.players:
            if p.status == PLAYER_ACTIVE:
                print(f"{p.name} {p.chip_count} ", end="")
        print()

    def betting_round(self, community_cards):
        preflop = len(community_cards) == 0
        current_player = self.dealer + 1
        pot = [0 for _ in range(len(self.players))]
        to_match = 0
        if preflop:
            # add blinds
            # all players start active so don't need to worry about folded positions
            sb = self.player_n(self.dealer + 1)
            pot[sb] += min(self.players[sb].chip_count, self.small_blind)
            self.players[sb].chip_count -= pot[sb]
            bb = self.player_n(self.dealer + 2)
            pot[bb] += min(self.players[bb].chip_count, self.big_blind)
            self.players[bb].chip_count -= pot[bb]
            current_player = self.player_n(self.dealer + 3)
            to_match = self.big_blind

        players_acted = [False if p.status == PLAYER_ACTIVE else True for p in self.players]
        while not all(players_acted) and self.active_player_count() > 1:
            if self.players[current_player].status == PLAYER_FOLDED:
                current_player = self.player_n(current_player + 1)
                continue
            self.display_players()
            bet = self.players[current_player].get_action(community_cards)
            total = bet+pot[current_player]
            action = ""
            if total < to_match:
                self.players[current_player].status = PLAYER_FOLDED
                action = "FOLD"
            else:
                if total == to_match:
                    if bet == 0:
                        action = "CHECK"
                    else:
                        action = "CALL"
                else:
                    action = f"RAISE {total}"
                    players_acted = [False if p.status == PLAYER_ACTIVE else True for p in self.players]
                    to_match = total
                self.players[current_player].chip_count -= bet
            players_acted[current_player] = True
            print(f"{self.players[current_player].name} {action}")
            current_player = self.player_n(current_player + 1)

        return sum(pot)

    def hand_end(self, pot):
        if self.active_player_count() == 1:
            for p in self.players:
                if p.status == PLAYER_ACTIVE:
                    winner = p
                    break
        else:
            ev = treys.Evaluator()
            winner = sorted([p for p in self.players if p.status == PLAYER_ACTIVE], lst=lambda x: ev.evaluate(self.community_cards, x.hand))

        winner.chip_count += pot

        if self.verbose:
            print(f"WINNER {winner.name} +{pot}")

    def hand(self):
        for p in self.players:
            p.status = PLAYER_ACTIVE

        pot = 0
        deck = treys.Deck()
        community_cards = []

        # deal
        for _ in range(2):
            for p in self.players:
                p.hand += deck.draw()
        # betting round
        if self.verbose:
            print("PREFLOP")
        pot += self.betting_round(community_cards)
        if self.active_player_count() == 1:
            self.hand_end(pot)
            return
        # flop
        community_cards = deck.draw(3)
        if self.verbose:
            print(f"\nFLOP  {treys.Card.ints_to_pretty_str(community_cards)}")
        # betting round
        pot += self.betting_round(community_cards)
        # turn and river
        for i in range(2):
            if self.active_player_count() == 1:
                self.hand_end(pot)
                return
            community_cards += deck.draw()
            # betting round
            if self.verbose:
                print(f"\n{('TURN ','RIVER')[i]} {treys.Card.ints_to_pretty_str(community_cards)}")
            pot += self.betting_round(community_cards)

        # showdown
        self.hand_end(pot)


p = Poker(
    (Player(10000, name="mabel"),
     Player(10000, name="joe"),
     Player(10000, name="gabriel"),
     Player(10000, name="ben")),
    500, 250, verbose=True)
p.hand()
