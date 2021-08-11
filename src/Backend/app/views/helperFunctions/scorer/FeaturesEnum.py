import enum

class FeaturesEnum(enum.IntEnum):
    NUM_USER_TOKENS = 0
    NUM_OTHER_USER_TOKENS = 1
    INTERSECTION_TOKENS = 2
    HOPS = 3
    TIME = 4
    FUZZY_SCORE = 5
