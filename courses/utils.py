
def options(amount=None):
    """Provides values for options which can be ORed together.

    If no amount is provided, returns a generator of ever growing numerical values starting from 1.
    If amount is provided, returns a amount-sized list of numerical values.
    """
    def generator():
        exp = 0
        cache = None
        while 1:
            if cache:
                cache = cache * 2
            else:
                cache = 2 ** exp
            yield cache
            exp += 1
    if amount is None:
        return generator()
    return [v for _, v in zip(range(amount), generator())]

def capitalized(string):
    "Capitalizes the first character in the given string."
    return string[0:1].upper() + string[1:].lower()
