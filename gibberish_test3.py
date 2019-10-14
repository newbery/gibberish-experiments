"""
This test checks for profanity by iterating through the possible gibberish
strings and testing for substring matches in the profanity list. This should
be much faster as we can quickly abandon substrings that don't exist in the
profanity list.

The expectation is that this should result in a smaller profanity list that
could be used to quickly filter the results from gibberish.

Maybe also we can calculate the probability of a profane gibberish word?
"""
from itertools import combinations, islice

from gibberish_util import gibberish_components
from alive_progress import alive_bar
from better_profanity import profanity


def beginnings(s):
    """ Generator that steps through all possible "beginning" strings"""
    return (s[:i + 1] for i in range(len(s)))


def endings(s):
    """ Generator that steps through all possible "ending" strings"""
    return (s[i:] for i in range(len(s)))


def get_profanity_list():
    """
    Get wordlist from library but filter out all words with substrings that
    are already in the list. No need to look for 'f**ker' if we are already
    filtering matches on 'f**k.'
    Let's also discard any with spaces as we don't have spaces in gibberish
    """
    lst = set(profanity.read_wordlist())
    for x, y in combinations(sorted(lst, key=len), 2):
        if x in y:
            lst.discard(y)
    for x in [w for w in lst if ' ' in w]:
        lst.discard(x)
    return lst


STACK = {}


def print_stack(more=''):
    print(', '.join(["%s:%s" % (k, v) for k, v in sorted(STACK.items())]), more)


def main(components=None):
    initials, vowels, finals, repeat_cnt, total_cnt = components or gibberish_components()
    end = ['']
    parts_sequence = [initials, vowels, finals, vowels, finals, end]
    parts_sequence_count = len(parts_sequence)
    profanity_list = get_profanity_list()
    profanity_found = set()
    beginning_profanity_list = {b for w in profanity_list for b in beginnings(w)}
        
    def profane(s):
        return s in profanity_list

    def profane_start(s):
        return s in beginning_profanity_list

    def consume_parts(index, parts, prefix='', skip=0):
        # print('PARTS INDEX: ', index)
        for part in parts:
            STACK[index] = part
            print_stack(':%s:%s:' % (prefix, skip))
            # print('PART: ', part)
            skip_ = skip
            fullstring = prefix + part
            
            # First iterate over the beginning substrings.
            substrings = beginnings(fullstring)
            for substring in substrings:
                if skip_:
                    substring = next(islice(substrings, skip_ - 1, skip_), '')
                    skip_ = 0
                # print(substring)
                if not profane_start(substring):
                    break
                if profane(substring):
                    profanity_list.remove(substring)
                    profanity_found.add(substring)
                    print('!!!!', substring)
                    break
            
            # Then recursively consume and append the next parts in the sequence.
            #
            # Make the current fullstring the new prefix but if the fullstring
            # is not the start of a profanity, first trim it by one character.
            # In this way, we can check if the trimmed result can now form the
            # start of a profanity.
            #
            # The `next_skip` is just to push the next substring iteration
            # forward past the parts of the string we've already tested.
            
            if profane_start(fullstring):
                current_string = fullstring
                next_skip = len(current_string)
            else:
                current_string = fullstring[1:]
                next_skip = 0
            next_index = index + 1
            if next_index < parts_sequence_count:
                for next_prefix in endings(current_string):
                    consume_parts(
                        next_index, parts_sequence[next_index],
                        next_prefix, next_skip)
        STACK.pop(index, None)
        print_stack(':%s:%s:' % (prefix, skip))

    with alive_bar() as bar:
        prefix = ''
        for index, parts in enumerate(parts_sequence):
            print(index)
            consume_parts(index, parts, prefix)
            bar()
        print('Done! Found %s profane words' % len(profanity_found))
        print(profanity_found)


def test():
    from gibberish_util import test_components
    main(test_components())


if __name__ == "__main__":
    main()
    # test()
