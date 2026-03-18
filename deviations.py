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
            19: {"6": "Ds"},  # Double soft 19 v 6
            18: {"2": "Ds"},  # Double soft 18 v 2
            18: {"3": "Ds"},  # Double soft 18 v 3
        },
        "pair": {},
    },
]
