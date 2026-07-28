from collections import Counter
class HandRank:
    def __init__(self, rank_name,rank_type, rank_value, kickers):
        self.rank_name = rank_name
        self.rank_type = rank_type 
        self.rank_value = rank_value 
        self.kickers = kickers  
    
    def __lt__(self, other):
        if self.rank_type != other.rank_type:
            return self.rank_type < other.rank_type
        if self.rank_value != other.rank_value:
            return self.rank_value < other.rank_value
        return self.kickers < other.kickers

    def __eq__(self, other):
        return (self.rank_type == other.rank_type and 
                self.rank_value == other.rank_value and 
                self.kickers == other.kickers)

class HandEvaluator: 
    suits = ['spades','hearts','diamonds','clubs']
    rank_types = {
        'ROYAL_FLUSH':9,
        'STRAIGHT_FLUSH':8,
        'FOUR_KIND':7,
        'FULL_HOUSE':6,
        'FLUSH': 5,
        'STRAIGHT': 4,
        'THREE_KIND': 3,
        'TWO_PAIR': 2,
        'ONE_PAIR':1,
        'HIGH_CARD':0
    }
    
    @classmethod
    def _rank_cards(cls,hole,community):
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
            rank_name = 'FOUR_KIND'
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
            rank_name = 'THREE_KIND'
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
        
        
    @classmethod
    def _is_royal_flush(cls,hole,community):
        all_cards = hole+community
        if len(all_cards) < 7:
            raise RuntimeError("Unexpected error: Hole+Community cards lesser than 7")
        
        for suit in cls.suits:
            same_suit_cards = cls._get_same_suit_cards(suit=suit,cards=all_cards)
            hand = sorted(same_suit_cards,reverse=True)[:5]
            if set([c.value for c in hand]) == {14,13,12,11,10}:
                return True
        return False
    
    @classmethod
    def _is_straight_flush(cls,hole,community):
        all_cards = hole+community
        for suit in cls.suits:
            same_suit_cards = cls._get_same_suit_cards(suit=suit,cards=all_cards)
            if len(same_suit_cards) < 5:
                continue
            
            for i in range(0,len(same_suit_cards)-4):
                hand = same_suit_cards[i:i+5]
                
                if cls._is_sequential(hand):
                    return True
        return False
    
    @classmethod
    def _is_four_kind(cls,hole,community):
        all_cards = sorted(hole+community,reverse=True)
        for i in range(len(all_cards)-3):
            to_check = all_cards[i:i+4]
            if len(to_check) != 4:
                raise RuntimeError("Unexpected Error in four of a kind check")
            
            four_of_kind = all(c == to_check[0] for c in to_check)
            if four_of_kind:
                return True
        
        return False
    
    @classmethod 
    def _is_full_house(cls,hole,community):
        all_cards = sorted(hole+community,reverse=True)
        for i in range(len(all_cards)-4):
            hand = all_cards[i:i+5]
            counts = Counter([c.value for c in hand])
            if sorted(counts.values()) == [2,3]:
                return True
        return False
    
    @classmethod
    def _is_flush(cls,hole,community):
        all_cards = hole+community
        suits = [card.suit for card in all_cards]
        counts = Counter(suits)
        return any(count >= 5 for count in counts.values())
    
    @classmethod
    def _is_straight(cls,hole,community):
        all_cards = sorted(hole+community,reverse=True)
        for i in range(0,len(all_cards)-4):
            hand = all_cards[i:i+5]
            if cls._is_sequential(hand):
                return True
        return False
    
    @classmethod
    def _is_three_kind(cls,hole,community):
        all_cards = hole+community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        return any(count >= 3 for count in counts.values())
        
    @classmethod
    def _is_two_pair(cls,hole,community):
        all_cards = hole + community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        return sum(1 for count in counts.values() if count >= 2) >= 2
    
    @classmethod
    def _is_one_pair(cls,hole,community):
        all_cards = hole + community
        ranks = [card.value for card in all_cards]
        counts = Counter(ranks)
        return sum(1 for count in counts.values() if count >= 2) >= 1
        
    @classmethod
    def _get_same_suit_cards(cls,suit,cards):
        return [c for c in cards if c.suit==suit]
    
    @classmethod
    def _is_sequential(cls,cards):
        vals = sorted([c.value for c in cards],reverse=True)
        uniq = set(vals)
        if len(vals) != len(uniq):
            return False
        return max(vals)-min(vals)+1 == len(uniq)
    
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
        highest_rank = max(hand)
        kickers = hand[1:5]
        
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
                highest_rank = max(highest_rank,high_card)
        
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
    
        
class ProbabilityEsitmator:
  pass