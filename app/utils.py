from re import split as re_split


def tokenize(text):
    """
    :param text:
    :return: a list of tokens
    """
    is_preposition = lambda _w: _w in ["de", "da", "do", "em", "e", "dos", "das"]

    result = []
    prep = None

    # Remove (a)
    words = filter(lambda x: bool(x), re_split('\W+', text.lower().replace(r"(a)", "")))

    for word in words:
        if not is_preposition(word):
            word = word.title()
            if prep:
                word = "%s %s" % (prep, word)
            prep = None

            result.append(word.strip())

        else:
            prep = word

    return result


def format_name(proper_name):
    """
    :param proper_name:
    :return:
    """
    return " ".join(tokenize(proper_name))
