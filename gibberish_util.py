"""
Return the gibberish components
"""
import string
import gibberish


# We won't call `generate_word` because for this test we are not interested
# in random words... we should generate all of the possible words.
# But we probably only need two syllables to locate any possible profanity.

def gibberish_components(path='components.yaml'):
    path = gibberish.database_path(path)
    f = open(path).read()
    components = gibberish.yaml.safe_load(f)

    initials = list(
        set(string.ascii_lowercase) -
        set('aeiou') -
        set('qxc') |
        set(sum(components['initials'], []))
    )

    finals = list(
        set(string.ascii_lowercase) -
        set('aeiou') -
        set('qxcsj') |
        set(sum(components['finals'], []))
    )

    vowels = list(
        set(sum(components['vowels'], []))
    )

    repeat_cnt = len(vowels) * len(finals)
    total_cnt = len(initials) * repeat_cnt**2
    return initials, vowels, finals, repeat_cnt, total_cnt


def test_components():
    initials = ['f', 'tt', 'ss']
    vowels = ['u', 'aa', 'i']
    finals = ['ck', 't', 'th', 'ss']
    repeat_cnt = len(vowels) * len(finals)
    total_cnt = len(initials) * repeat_cnt**2
    return initials, vowels, finals, repeat_cnt, total_cnt
