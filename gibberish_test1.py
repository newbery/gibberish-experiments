"""
A brute force test to see if any gibberish words trigger the profanity_filter
"""
from gibberish_util import gibberish_components
from alive_progress import alive_bar
from profanity_filter import ProfanityFilter


def main(components=None):
    initials, vowels, finals, repeat_cnt, total_cnt = components or gibberish_components()
    pf = ProfanityFilter()
    cnt = 0
    profane_cnt = 0
    with alive_bar(total_cnt) as bar:
        for i in initials:
            for v in vowels:
                for f in finals:
                    prefix = ''.join([i, v, f])
                    if pf.is_profane(prefix):
                        print(cnt, 'All %s words beginning with "%s..."' % (repeat_cnt, prefix))
                        cnt += repeat_cnt
                        profane_cnt += repeat_cnt
                        bar(incr=repeat_cnt)
                        continue
                    for v2 in vowels:
                        for f2 in finals:
                            cnt += 1
                            word = ''.join([prefix, v2, f2])
                            if pf.is_profane(word):
                                profane_cnt += 1
                                print(cnt, word)
                            bar()
    print('Done! Found %s profane words in %s total' % (profane_cnt, cnt))


def test():
    from gibberish_util import test_components
    main(test_components())


if __name__ == "__main__":
    main()
