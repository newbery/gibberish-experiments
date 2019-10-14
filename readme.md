# A gibberish usecase

Requirement: Generate unique urls (for a referral reward program) that are
relatively easy to remember and not too intimidating, like so:

```
    https://domain.com/referral/[something simple]
```

One possibility is to allow the user to just specify their own text but
this may potentially be abused by impolite or unscrupulous users.

Another possibility is to randomly generate a string from real words or from
word-like "gibberish". Real words strung together randomly can potentially
result in unintended meanings so random gibberish seems like a good candidate.
It turns out there is nice python library to generate gibberish called,
naturally enough, `gibberish`:

    https://pypi.org/project/gibberish/

It's easy to use and generates gibberish that seems to satisfy the requirement.

```python
  > from gibberish import Gibberish
  > gib = Gibberish()
  > 
  > gib.generate_word()
  'naands'
  >
  > gib.generate_word(vowel_consonant_repeats=2)
  'duxery'
```

However, it seems possible to generate duplicates and profane words.
Let's study this... 


## Duplicates

We can count the number of components that are used to form gibberish words
from `./gibberish/database/components.yaml` and `./gibberish/__init__.py`:

  initials: 98 items
  vowels: 39 items
  finals: 103 items

Words are constructed from 'initial' + 'vowel' + 'final'
(plus another 'vowel' + 'final' for each `vowel_consonent_repeats`>1)

For N syllables: 98 x (39 x 103) ^ N = 98 x 4017^N

  1 syllable --> 393,666 words  
  2 syllable --> 1,581,356,322 words  
  3 syllable --> 6,352,308,345,474 words  

So a random two-syllable gibberish word has approximately a 1:1.6-billionth of
a probability of being a duplicate of a single previous choice. Of course
this probability slowly increases as the list of previous choices increases.
Whether this is a problem depends on how many choices are likely to be collected
and how conflicts are detected and resolved.

In this particular usecase, the number of urls likely to be generated does
not seem likely to exceed 100,000 over the lifetime of the service and they
would be stored in a relational database table with uniqueness enforced.
It should be a simple matter to handle the non-unique error case and just
regenerate the word and try again.


## Profanity

Which is the fastest and most accurate profanity checker library for local
testing?

Found an interesting blog post (from the author of `profanity-check`):
https://towardsdatascience.com/building-a-better-profanity-detection-library-with-scikit-learn-3638b2f2c4c2

The top contenders appear to be:

 - https://pypi.org/project/profanity/  
   Checks against a 32 word list. Fast.
   
 - https://pypi.org/project/better-profanity/  
   Checks against a 317 word list. Claims to be faster than 'profanity'
   
 - https://pypi.org/project/profanityfilter/  
   Checks against a 418 word list. Unknown speed.
   Looking through the code, I see a few places where optimization would
   have sped it up... a sign that it is probably slow?
   
 - https://pypi.org/project/profanity-filter/  
   Uses machine learning. Very slow
   
 - https://pypi.org/project/profanity-check/  
   Also uses machine learning. Fast

Since I'm curious about machine learning approaches, I decided to start
with those. The results were not great... maybe this usecase is not ideal
for a ML solution. For the third attempt, I settled for a non-ML solution
which seems better... but still not good enough.


## Attempt 1: Brute force test with `profanity-filter`

A brute force test with `profanity-filter` where the script generates all
possible gibberish words and tested each for profanity.

Perhaps I'm not using this one correctly. It started to catch way too many
false positives. It was also very slow. The progress meter estimated at least
25 days to complete. Needless to say, I stopped the run before completion.

```shell
  $ python3 -m venv ./env
  $ source ./env/bin/activate
  $ 
  $ pip install gibberish
  $ pip install alive-progress
```

```shell
  $ pip install profanity-filter
  $ python -m spacy download en
  $ 
  $ brew install hunspell
  $ sudo ln -sf /usr/local/lib/libhunspell-1.7.a /usr/local/lib/libhunspell.a
  $ ln -s /usr/local/Cellar/hunspell/1.7.0_2/lib/libhunspell-1.7.0.dylib /usr/local/Cellar/hunspell/1.7.0_2/lib/libhunspell.dylib
  $ pip install -U -r https://raw.githubusercontent.com/rominf/profanity-filter/master/requirements-deep-analysis.txt
  $ pip install -U -r https://raw.githubusercontent.com/rominf/profanity-filter/master/requirements-pymorphy2-ru.txt
  $ 
  $ pushd ./env/lib/python3.7/site-packages/profanity_filter/data/
  $ wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/en/en_US.aff
  $ wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/en/en_US.dic
  $ mv en_US.aff en.aff
  $ mv en_US.dic en.dic
  $ popd
```

```shell
  $ python ./gibberish_test1.py
```

## Attempt 2: Brute force test with `profanity-check`

Another brute force test similar to the first attempt but using `profanity-check`
instead.

Better. The set up was much simpler and I did not see any false positives.
But it also ran slow. The progress meter estimated 22 days to complete.
Again, I stopped the run early and moved on to another solution.


```shell
  $ python3 -m venv ./env
  $ source ./env/bin/activate
  $ 
  $ pip install gibberish
  $ pip install alive-progress
```

```shell
  $ pip install profanity-check
```

```shell
  $ python ./gibberish_test2.py
```

## Attempt 3: Substring iterate test using wordlist from `better-profanity`

The biggest issue with the brute force method is the shear number of gibberish
words the scripts were generating. I looked for a better way to iterate over the
possible words by testing the substrings incrementally and then terminating
a branch search whenever a matching substring was found. The theory being that
many of the words shared matching profane substrings and this would eliminate
the number of total tests.

And since we are testing substrings, it seems easier to just do a simple test
to see if the substring exists in a list of profane words. The `better-profanity`
library appeared to have the best word list for this purpose.

The first try with this approach is not much better but it shows promise.
Unfortunately, because of the nature of this solution, it's not clear how
to estimate time to completion. I let it run for a couple of hours and it
quickly came up with about 50 matches but then tapered off.

I suspect the iteration is doing more work than necessary. There is probably
some more tricks I can do to keep track of abandoned branches that repeat
themselves during the iterations. I'll think about this and maybe come back
with another attempt.

One interesting result for this attempt is that after the source profanity list
was filtered to include only "root" words and no spaces, the list went from
315 words down to 151.


```shell
  $ python3 -m venv ./env
  $ source ./env/bin/activate
  $ 
  $ pip install gibberish
  $ pip install alive-progress
```

```shell
  $ pip install better-profanity
```

```shell
  $ python ./gibberish_test3.py
```

## Attempt 4: An improved version of attempt 3

[work in progress]


## Conclusion

Attempt 3 shows promise but still too slow. A work in progress...
