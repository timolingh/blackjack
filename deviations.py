"""
Deviation overrides for playing decisions.

Each entry in DEVIATION_LEVELS is merged in order to build the active
deviation map:
- Index 0 is applied when the running count is greater than zero.
- Index n (where n >= 1) is additionally applied when the true count
  is at least n. Later dictionaries override earlier ones on conflicts.

Structure per level:
{
    "hard": {16: {"10": "S"}},
    "soft": {18: {"2": "S"}},
    "pair": {"9": {"7": "S"}}
}

The default placeholders are empty; populate them with your preferred
deviations.
"""

DEVIATION_LEVELS: list[dict[str, dict]] = [
    # running count > 0
    {
        "hard": {
            15: {"A": "Rh"},  # Surrender 15 v A at TC >= -1 (base positive tier)
            16: {"10": "S"},  # Stand 16 v 10 on any positive running count
        },
        "soft": {},
        "pair": {},
    },
    # true count >= 1 but < 2
    {
        "hard": {
            11: {"A": "Dh"},  # Double 11 v Ace (H17) at TC >= 1
            9: {"2": "Dh"},   # Double 9 v 2
        },
        "soft": {
            19: {"5": "Ds"},  # Double soft 19 v 5 at TC >= 1
            17: {"2": "Ds"},  # Double soft 17 v 2 at TC >= 1
        },
        "pair": {},
    },
    # true count >= 2 but < 3
    {
        "hard": {
            12: {"3": "S"},  # Stand 12 v 3 at TC >= 2
            8: {"6": "Dh"},  # Double 8 v 6 at TC >= 2
        },
        "soft": {},
        "pair": {},
    },
    # true count >= 3 but < 4
    {
        "hard": {
            16: {"A": "S"},  # Stand 16 v Ace at TC >= 3
            12: {"2": "S"},  # Stand 12 v 2 at TC >= 3
            10: {"A": "Dh"},  # Double 10 v Ace at TC >= 3
        },
        "soft": {
            19: {"4": "Ds"},  # Double soft 19 v 4 at TC >= 3
        },
        "pair": {},
    },
    # true count >= 4 but < 5
    {
        "hard": {
            16: {"9": "S"},  # Stand 16 v 9 at TC >= 4
            10: {"10": "Dh"},  # Double 10 v 10 at TC >= 4   
        },
        "soft": {},
        "pair": {
            "10": {"6": "P"},  # Split 10s v 6 at TC >= 4
        },
    },
    # true count >= 5
    {
        "hard": {
        },
        "soft": {},
        "pair": {
            "10": {"5": "P"},  # Split 10s v 5 at TC >= 5
        },
    },
    # true count >= 6
    {
        "hard": {},
        "soft": {},
        "pair": {
            "10": {"4": "P"},  # Split 10s v 4 at TC >= 6
        },
    }

]

# Negative deviation tiers (running count < 0 and true count <= -1)
# Index 0 applies when running count is negative; subsequent indexes apply
# when true count is at or below the corresponding negative threshold.
NEGATIVE_DEVIATION_LEVELS: list[dict[str, dict]] = [
    # running count < 0
    {
        "hard": {
            16: {"10": "H"},  # Hit 16 v 10 on any negative running count
        }, 
        "soft": {
            19: {"6": "S"}, # Stand soft 19 v 6 on any negative running count
        }, 
        "pair": {}
    },  
    # true count <= -1
    {
        "hard": {
            13: {"2": "H"},  # Hit 13 v 2 at TC <= -1
            16: {"9": "H"},   # Hit 16 v 9 at TC <= -1
        }, 
        "soft": {}, 
        "pair": {}
    },  
]
