# blackjack.py

from math import comb
import random 
import itertools
import re 
import numpy as np
from copy import deepcopy
from functools import reduce


# estimate the prob of a specific number k using the hypergeometric distribution 
def p_hg(K,k,N,n):
    return comb(K,k) * comb(N-K,n-k) / comb(N,n)


class Card:

    def determine_if_ace(self):
        
        if self.rank == "A":
            self.is_ace = True
        else:
            self.is_ace = False
        return self.is_ace


    def __init__(self,rank,suit=None):
        
        self.rank = str(rank) # A,2-10,J,Q,K
        self.suit = suit # S,C,H,D
        self.determine_if_ace()


    def get_value(self): #will_bust=False
        
        num = re.search(
            "([0-9]*)",
            self.rank
            )[0]
        
        if num:
            self.value = int(num)
        else:
            face = re.search(
                "([JQK]*)",
                self.rank,
                flags=re.IGNORECASE
                )[0].upper()
            
            if face:
                self.value = 10
            else:
                ace = re.search(
                    "(A*)",
                    self.rank,
                    flags=re.IGNORECASE
                    )[0].upper()
                if ace:
                    self.value = Ace() 
                    # TODO self.value = Ace() # context ddependent 

        return self.value


    def __repr__(self):
        return self.rank + "," + self.suit


    def __str__(self):
        return self.rank + "," + self.suit



class Deck:

    def __init__(self):
        
        ranks = [str(i+1) for i in range(1,10)] + ["J","Q","K","A"]
        suits = ["H","D","C","S"]
        # creates a standard 52 card deck 
        self.cards = [Card(r,s) for r,s in itertools.product(ranks,suits)]
        

    def shuffle(self,returns="self"):
        
        random.shuffle(self.cards)
        if returns=="cards":
            return self.cards
        elif returns=="self":
            return self


    def draw_random_cards(self,number:int):
        
        drawn = list()
        for _ in range(number):
            drawn.append(self.cards.pop(0))
        return drawn
    

    def draw_specific_cards(self,cards_to_pull):
        
        if not isinstance(cards_to_pull,list):
            cards_to_pull = [cards_to_pull]

        drawn = list()
        for deck_i,deck_card in enumerate(self.cards):
            for card_to_pull in cards_to_pull:
                rank_same = (deck_card.rank == card_to_pull.rank)
                suit_same = (deck_card.suit == card_to_pull.suit)
                if rank_same and suit_same:
                    drawn.append(self.cards.pop(deck_i))
                    continue 

        return drawn


    # in process, remove 
    def remove(self,cards_to_pull,setting="cards"):
        
        self.draw_specific_cards(cards_to_pull)

        if setting=="cards":
            return self.cards
        elif setting=="self":
            return self


    def find_rank(self,rank, just_suits=False):
        
        if just_suits:
            return [card.suit for card in self.cards if card.rank==rank]
        else:
            return [card for card in self.cards if card.rank==rank]


class Hand():

    bust_threshold=22

    def __init__(self,deck,number_to_draw:int=2,drawn_hand:list=None,random:bool=False):
        
        if drawn_hand is not None:
            self.hand = deck.draw_specific_cards(drawn_hand)
        else:
            random = True

        if random:
            self.hand = deck.draw_random_cards(number_to_draw)


    def get_hand_value(self):

        sum_sans_ace = sum([card.get_value() for card in self.hand if not card.is_ace])
        self.value = sum_sans_ace
        ace_count = sum([card.is_ace for card in self.hand])
        # ace iterate, starts with highest, then goes to lowest
        bust = True
        for combo in itertools.combinations_with_replacement([11,1],r=ace_count):
            if (self.value + sum(combo)) >= self.bust_threshold:
                continue
            else: 
                self.value += sum(combo)
                bust = False
                break 
        if bust:
            self.value += sum(combo)

        return self.value    


    def draw_random_cards(self,number,deck,returns="self"):
  
        deck.shuffle()
        drawn = deck.draw_random_cards(number)
        self.hand += drawn

        if returns == "self":
            return self
        elif returns == "cards":
            return hand.hand
        elif returns == "new":
            return drawn


    def draw_specific_cards(self,cards_to_pull,deck):
        self.hand += deck.draw_specific_cards(cards_to_pull)



def simulate_hand_draw(number_drawn=2,hand=None,deck=None):
    
    if deck is not None:
        deck = deepcopy(deck)
    else:
        deck = Deck()

    if hand is not None:
        hand = deepcopy(hand)
        hand.draw_random_cards(number_drawn,deck)
        hand_value = hand.get_hand_value()
    else:
        hand_value = Hand(deck.shuffle("self"),number_drawn).get_hand_value()

    return hand_value


def simulate_hand_draws(number_drawn=2,niters=1e4,hand=None,deck=None,track=True):
    
    niters = int(niters)
    hand_draws = list()
    for i in range(niters):
        if track: # progress tracker 
            marg = round(niters)/100
            perc = i/marg
            if niters % 100 == 0:
                if perc % 5 == 0:
                    print(f"{i} iterations ({perc}%) complete")
        hand_draws.append(simulate_hand_draw(number_drawn,hand=hand,deck=deck))
    
    return hand_draws


# take a list of scores from simulate functions and get probability of each score as a dictionary
def compile_probs(hand_draws,normalize=True):
    
    values, counts = np.unique(np.array(hand_draws),return_counts=True)
    if normalize:
        counts = counts/np.sum(counts)
    values = [int(value) for value in values]
    return dict(zip(values, counts))


# if the dealer draws n cards, what's the probability distribution?
def simulate_prob_dist_from_deck(deck,number_drawn=2,niters=1e4,track=True):

    return compile_probs(
        simulate_hand_draws(
            number_drawn=number_drawn,
            deck=deck,
            niters=niters,
            track=track
            )
        )

# given your particular hand and random draws by the house, what's the probability of different outcomes?
def compare_prob_hand_to_house(hand,deck,n_drawn_by_house=2,house_niters=1e4,track=True): # currently redundant to include both 
    
    hand_value = hand.get_hand_value()
    house_value_p_dict = simulate_prob_dist_from_deck(
        deck=deck,number_drawn=n_drawn_by_house,niters=house_niters,track=track
        )
    win_p, lose_p, draw_p, bust_p = 0.,0.,0.,0.
    if hand_value < hand.bust_threshold:
        for house_value,p in house_value_p_dict.items():
            if hand_value > house_value:
                win_p += p
            elif hand_value < house_value:
                lose_p += p
            elif hand_value == house_value:
                draw_p += p
    else:
        bust_p += 1.

    prob_d = {"win":win_p,"lose":lose_p,"draw":draw_p,"bust":bust_p}

    return prob_d


def flatten(l):

    return [item for sublist in l for item in sublist]


def reducer(accumulator, element):

    for key, value in element.items():
        accumulator[key] = accumulator.get(key, 0) + value
    return accumulator


# get unique keys from a list of dictionaries 
def get_unique_d_keys(ds:list):

    return sorted(list(set(flatten([list(i.keys()) for i in ds]))))


def avg_dicts(ds:list):

    d_avg = reduce(reducer,ds,{})
    ks=get_unique_d_keys(ds)
    n=len(ds)
    for k in ks:
        sum_p=0.
        for d in ds:
            sum_p+=d.get(k,0)
        avg_p=sum_p/n
        d_avg[k]=avg_p
    return d_avg

# given you randomly draw a card on top of your existing hand, what are the probabilities of different outcomes
def compare_prob_hit_to_house(base_hand,deck,n_drawn_by_house=2,
                              hand_niters=1e2,house_niters=1e2,
                              track_outer=True,track_inner=False):
    
    hand_niters=int(hand_niters)
    p_ds = list()
    for i in range(hand_niters):
        if track_outer: # progress tracker 
            marg = round(hand_niters)/100
            perc = i/marg
            if hand_niters % 100 == 0:
                if perc % 5 == 0:
                    print(f"{i} iterations ({perc}%) complete")

        hit_hand = deepcopy(base_hand)
        deck_i = deepcopy(deck)
        hit_hand = hit_hand.draw_random_cards(1,deck_i,"self")
        p_d = compare_prob_hand_to_house(
            hit_hand,deck_i,n_drawn_by_house,house_niters, track=track_inner
            )
        p_ds.append(p_d)
    d_avg = avg_dicts(p_ds)
    
    return d_avg

# so, should you hit or stay?
def hit_results(hand,deck,print_=True):
    calc_gain_loss_ratio = lambda d: d["win"]/(d["lose"]+d["bust"])
    calc_p_win_sans_draws = lambda d: d["win"]/(d["win"]+d["lose"]+d["bust"])

    
    stay_hand = deepcopy(hand)
    stay_prob_d = compare_prob_hand_to_house(stay_hand,deck)
    hit_base_hand = deepcopy(hand)
    hit_prob_d = compare_prob_hit_to_house(hit_base_hand,deck)

    stay_glr = calc_gain_loss_ratio(stay_prob_d)
    hit_glr = calc_gain_loss_ratio(hit_prob_d)

    stay_win_no_draws = calc_p_win_sans_draws(stay_prob_d)
    hit_win_no_draws = calc_p_win_sans_draws(hit_prob_d)

    if print_:
        print(f"Your hand contains:",[card.rank for card in hand.hand])
        print(f"If you stay, your chance of winning is \
{round(stay_win_no_draws*100,1)}% (excluding draws)")
        print(f"If you hit, your chance of winning is \
{round(hit_win_no_draws*100,1)}% (excluding draws)")
              
        if stay_win_no_draws > hit_win_no_draws:
            print("You should stay.")
        elif stay_win_no_draws < hit_win_no_draws:
            print("You should hit.")
        else:
            print("Follow your heart. The odds are the same either way.")

    if stay_win_no_draws > hit_win_no_draws:
        return "stay"
    elif stay_win_no_draws < hit_win_no_draws:
        return "hit"
    else:
        return "immaterial"


def check_if_in_deck(rank,suit,deck):
    for card in deck.cards:
        rank_same = (rank == card.rank)
        suit_same = (suit == card.suit)
        if rank_same and suit_same:
            return True
    return False 


# purpose: wrapper function to allow user to interact without specifying a suit 
def c(rank,suit=None,deck=None): 
    rank = str(rank)

    if suit is None:
        if deck is not None:
            suits = deck.find_rank(rank,just_suits=True)
            if len(suits) > 0:
                suit = random.choice(suits)
                return Card(rank,suit)
            else:
                raise ValueError(f"no cards of rank {rank} remain in this deck")

        else:
            suits = ["D","C","S","H"]
            suit = random.choice(suits)

    return Card(rank,suit)


if __name__ == "__main__":

    deck = Deck().shuffle()

    # shows results from 2 randomly drawn cards
    hand = Hand(deck=deck,number_to_draw=2) 

    # or, uncomment below and specify your own cards
    # drawn_cards = [c("A"),c("9")]
    # hand = Hand(deck=deck,drawn_hand=drawn_cards) 

    hit_results(hand,deck)