from collections import Counter
from GameElements import Card
from .HandRank import HandRank

class HandEvaluator:     
    suits = ['spades','hearts','diamonds','clubs']
    rank_types = {
        'ROYAL_FLUSH':9,
        'STRAIGHT_FLUSH':8,
        'FOUR_OF_A_KIND':7,
        'FULL_HOUSE':6,
        'FLUSH': 5,
        'STRAIGHT': 4,
        'THREE_OF_A_KIND': 3,
        'TWO_PAIR': 2,
        'ONE_PAIR':1,
        'HIGH_CARD':0
    }
    
    @classmethod
    def rank_cards(cls,hole,community):
        if cls._is_royal_flush(hole,community):
            rank_name = 'ROYAL_FLUSH'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = 14, []
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)            
        
        if cls._is_straight_flush(hole,community):
            rank_name = 'STRAIGHT_FLUSH'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_straight_flush_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)   
        
        if cls._is_four_kind(hole=hole,community=community):
            rank_name = 'FOUR_OF_A_KIND'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_four_kind_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        if cls._is_full_house(hole=hole,community=community):
            rank_name = 'FULL_HOUSE'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_full_house_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        if cls._is_flush(hole=hole,community=community):
            rank_name='FLUSH'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_flush_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        if cls._is_straight(hole=hole,community=community):
            rank_name = 'STRAIGHT'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_straight_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        if cls._is_three_kind(hole=hole,community=community):
            rank_name = 'THREE_OF_A_KIND'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_three_kind_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        if cls._is_two_pair(hole=hole,community=community):
            rank_name = 'TWO_PAIR'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_two_pair_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        if cls._is_one_pair(hole=hole,community=community):
            rank_name = 'ONE_PAIR'
            rank_type = cls.rank_types[rank_name]
            rank_value,kickers = cls._get_one_pair_rank_kickers(hole,community)
            return HandRank(rank_name=rank_name,rank_type=rank_type,
                            rank_value=rank_value, kickers=kickers)
        
        rank_name = 'HIGH_CARD'
        rank_type = cls.rank_types[rank_name]
        rank_value, kickers = max(hole),min(hole)
        return HandRank(rank_name=rank_name,rank_type=rank_type,
                        rank_value=rank_value, kickers=kickers)
        
        
    @staticmethod
    def _is_royal_flush(hole,community):
        suits = ['spades','hearts','diamonds','clubs']
        all_cards = hole+community
        if len(all_cards) < 7:
            raise RuntimeError("Unexpected error: Hole+Community cards lesser than 7")
        
        for suit in suits:
            same_suit_cards = HandEvaluator._get_same_suit_cards(suit=suit,cards=all_cards)
            hand = sorted(same_suit_cards,reverse=True)[:5]
            if set([c.value for c in hand]) == {14,13,12,11,10}:
                return True
        return False
    
    @staticmethod
    def _is_straight_flush(hole,community):
        all_cards = hole+community
        suits = ['spades','hearts','diamonds','clubs']
        for suit in suits:
            same_suit_cards = HandEvaluator._get_same_suit_cards(suit=suit,cards=all_cards)
            if len(same_suit_cards) < 5:
                continue
            
            for i in range(0,len(same_suit_cards)-4):
                hand = same_suit_cards[i:i+5]
                
                if HandEvaluator._is_sequential(hand):
                    return True
        return False
    
    @staticmethod
    def _is_four_kind(hole,community):
        all_cards = sorted(hole+community,reverse=True)
        for i in range(len(all_cards)-3):
            to_check = all_cards[i:i+4]
            if len(to_check) != 4:
                raise RuntimeError("Unexpected Error in four of a kind check")
            
            four_of_kind = all(c == to_check[0] for c in to_check)
            if four_of_kind:
                return True
        
        return False
    
    @staticmethod 
    def _is_full_house(hole,community):
        all_cards = sorted(hole+community,reverse=True)
        ranks =  [c.value for c in all_cards]
        rank_counts = Counter(ranks)
        
        #iterate over all possible pairs in rank_counts
        #and check if 3,2 or 2,3 exists
        for rank1,count1 in rank_counts.items():
            #check if rank forms 'triplet' part of full house
            if count1 < 3:
                continue
            for rank2,count2 in rank_counts.items():
                # same rank cannot form a full house, skip
                if rank1 == rank2:
                    continue
                
                #check if 
                if count2 < 2:
                    continue
            
                #rank1 has at least count=3, rank2 has at least count=2 i.e full house
                return True
        
        return False
        
    @staticmethod
    def _is_flush(hole,community):
        all_cards = hole+community
        suits = [card.suit for card in all_cards]
        counts = Counter(suits)
        return any(count >= 5 for count in counts.values())
    
    @staticmethod
    def _is_straight(hole,community):
        all_cards = sorted(hole+community,reverse=True)
        
        if 14 in [c.value for c in all_cards]:
            low_ace = Card('diamond',1) #arbitrary suit doesnt matter for straight calculation
            all_cards.append(low_ace)
        
        for i in range(0,len(all_cards)-4):
            hand = all_cards[i:i+5]
            if HandEvaluator._is_sequential(hand):
                return True
        return False
    
    @staticmethod
    def _is_three_kind(hole,community):
        all_cards = hole+community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        return any(count >= 3 for count in counts.values())
        
    @staticmethod
    def _is_two_pair(hole,community):
        all_cards = hole + community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        return sum(1 for count in counts.values() if count >= 2) >= 2
    
    @staticmethod
    def _is_one_pair(hole,community):
        all_cards = hole + community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        return sum(1 for count in counts.values() if count >= 2) >= 1
        
    @staticmethod
    def _get_same_suit_cards(suit,cards):
        return [c for c in cards if c.suit==suit]
    
    @staticmethod
    def _is_sequential(cards):
        ranks = sorted([c.value for c in cards])
        
        uniq = set(ranks)
        if len(ranks) != len(uniq):
            return False
        
        is_sequence = (max(ranks) - min(ranks) +1 == len(uniq))
        
        return is_sequence
    
    @staticmethod
    def _get_straight_flush_rank_kickers(hole,community):
        highest_rank = 0
        kickers = []
        
        suits = ['spades','hearts','diamonds','clubs']
        all_cards = hole+community
        
        for s in suits:
            same_suit = [c for c in all_cards if c.suit == s]
            if len(same_suit) < 5:
                continue
        
        for i in range(0,len(same_suit)-4):
            hand = same_suit[i:i+5]
            
            if HandEvaluator._is_sequential(hand):
                high_card = max(hand)
                highest_rank = max(high_card.value,highest_rank)
                kickers = []
        
        return highest_rank,kickers
    
    @staticmethod
    def _get_four_kind_rank_kickers(hole,community):
        highest_rank = 0
        kicker = []
        
        all_cards = sorted(hole+community,reverse=True)
        for i in range(len(all_cards)-3):
            to_check = all_cards[i:i+4]
            if len(to_check) != 4:
                raise RuntimeError("Unexpected Error in four of a kind check")
            
            four_of_kind = all(c == to_check[0] for c in to_check)
            if four_of_kind:
                high_card = to_check[0].value
                highest_rank = max(highest_rank,high_card)
        
        return highest_rank,kicker
    
    @staticmethod
    def _get_full_house_rank_kickers(hole,community):
        highest_rank = 0
        kickers = []
        all_cards = sorted(hole+community,reverse=True)
        for i in range(len(all_cards)-4):
            hand = all_cards[i:i+5]
            counts = Counter([c.value for c in hand])
            if sorted(counts.values()) == [2,3]:
                triple_card_rank = next(k for k, v in counts.items() if v == 3)
                highest_rank = max(triple_card_rank,highest_rank)
                
                double_card_rank =  next(k for k,v in counts.items() if v == 2)
                kickers = double_card_rank
        
        return highest_rank,kickers
    
    @staticmethod
    def _get_flush_rank_kickers(hole,community):
        all_cards = hole+community
        suits = [card.suit for card in all_cards]
        counts = Counter(suits)
        
        target_suit = next(suit for suit,count in counts.items() if count >=5)
        hand =  sorted([c for c in all_cards if c.suit == target_suit])
        highest_card = max(hand)
        highest_rank = highest_card.value
        remaining_cards = hand[1:5]
        kickers = [c.value for c in remaining_cards]
        
        return highest_rank,kickers
    
    @staticmethod
    def _get_straight_rank_kickers(hole,community):
        all_cards = sorted(hole+community,reverse=True)
        
        highest_rank = 0
        kickers = []
        for i in range(0,len(all_cards)-4):
            hand = all_cards[i:i+5]
            if HandEvaluator._is_sequential(hand):
                high_card = max(hand)
                highest_rank = max(highest_rank,high_card.value)
        
        return highest_rank,kickers
    
    @staticmethod
    def _get_three_kind_rank_kickers(hole,community):
        all_cards = sorted(hole+community,reverse=True)
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        highest_rank = max(k for k,v in counts.items() if v==3)
        kickers = sorted([k for k in counts.keys() if k!=highest_rank],reverse=True)
        
        return highest_rank,kickers
    
    @staticmethod
    def _get_two_pair_rank_kickers(hole,community):
        all_cards = hole + community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)

        pair_ranks = sorted([r for r, c in counts.items() if c >= 2], reverse=True)
        first_pair = pair_ranks[0]
        second_pair = pair_ranks[1]

        remaining = ranks.copy()
        for rank in (first_pair, second_pair):
            remaining.remove(rank)
            remaining.remove(rank)

        s = sorted(remaining, reverse=True)
        
        kickers = [second_pair] + s
        return first_pair, kickers    
    
    @staticmethod
    def _get_one_pair_rank_kickers(hole,community):
        all_cards = sorted(hole+community,reverse=True)
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        highest_rank = max(k for k,v in counts.items() if v==2)
        kickers = sorted([k for k in counts.keys() if k!=highest_rank],reverse=True)
                
        return highest_rank,kickers
    
