"""
A brute force test to see if any gibberish words trigger the profanity_check
"""
from gibberish_util import gibberish_components
from alive_progress import alive_bar
from profanity_check import predict


def profane(text):
    return predict([text])[0] == 1


def main(components=None):
    initials, vowels, finals, repeat_cnt, total_cnt = components or gibberish_components()
    cnt = 1
    profane_cnt = 0
    with alive_bar(total_cnt, calibrate=800) as bar:
        for i in initials:
            for v in vowels:
                for f in finals:
                    prefix = ''.join([i, v, f])
                    if profane(prefix):
                        print('All %s words beginning with "%s..."' % (repeat_cnt, prefix))
                        profane_cnt += repeat_cnt
                        cnt += repeat_cnt
                        bar(incr=repeat_cnt)
                        continue
                    for v2 in vowels:
                        for f2 in finals:
                            word = ''.join([prefix, v2, f2])
                            if profane(word):
                                print('"%s"' % word)
                                profane_cnt += 1
                            cnt += 1
                    bar(incr=repeat_cnt)
    print('Done! Found %s profane words in %s total' % (profane_cnt, cnt))


def test():
    from gibberish_util import test_components
    main(test_components())


if __name__ == "__main__":
    main()
