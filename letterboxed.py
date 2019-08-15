#!python3
#
# solutions finder for https://www.nytimes.com/puzzles/letter-boxed
#
# run like this: BOARD=OGA-PIH-KNT-ELS python3 letterboxed.py
# for this example, it found [SPOTLIGHT TAKEN], [SPEAKING GHOSTLIKE],
#    [OPENINGS SHOPTALK] and [HEPATITIS SONGLIKE] among others.
#
# notes:
# - tries to find solutions with small numbers of words, ideally 1-2
# - tries to use long words with large number of unique letters
# - if you provide a list of "popular" words, it'll try to use those first
#
# optimization: set environment variable MINLEN to only use words with
# that many letters or more
#
# PRs welcome.  To reach me for other things, try LinkedIn.com/in/adamsah
#

import os, re, sys, time
from pytrie import StringTrie

board = re.sub('[^A-Z-]', '', os.environ.get("BOARD", "OGA-PIH-KNT-ELS").upper())
letters = re.sub('[^A-Z]', '', board)
letterset = set(letters)
board_array = board.split('-')


# download from https://github.com/first20hours/google-10000-english
popular_long_words = open('google-10000-english-usa-no-swears-long.txt').read().splitlines()
popular_medium_words = open('google-10000-english-usa-no-swears-medium.txt').read().splitlines()
popular_words = set([w.upper() for w in (popular_long_words + popular_medium_words)])

# download from: https://www.google.com/search?q=SOWPODS+github
words = open('SOWPODS.txt').read().splitlines()

print(f"loaded {len(words)} words")

words = [word for word in words if letterset >= set(word)]
print(f"subsetted to {len(words)} words: {words[0:20]}...")

# optimization
minlen = int(os.environ.get("MINLEN", "4"))
words = [word for word in words if len(word) >= minlen]

words_trie=StringTrie() 
for word in words:
  words_trie[word] = word
words_set=set(words)

possible_next_letters = {}
for side in board_array:
  other_letters = letterset - set(side)
  print(f"{side}: {other_letters}")
  for ltr in side:
    possible_next_letters[ltr] = other_letters

def word_tree(prefix):
  last_ltr = prefix[-1]
  next_ltrs = possible_next_letters[last_ltr]
  words = []
  if len(prefix)>20: return words # just in case...
  for ltr in next_ltrs:
    next_prefix = prefix + ltr
    if len(next_prefix) >= 3 and next_prefix in words_set:
      words.append(next_prefix)
    #if words_trie.has_key(next_prefix):
    if len(words_trie.values(next_prefix)) > 0:
      #print(f"{prefix}: found {next_prefix} in words_trie")
      words += word_tree(next_prefix)
  return words

words_by_starting_ltr = dict([ (ltr, []) for ltr in letters ])
cnt = 0;
last_time = int(time.time())
best_len_so_far = 2
def find_words(words, addword):
  global cnt, last_time, best_len_so_far
  newlist = words + [addword]
  # safety - should never happen given set-check below
  ltrs_visited = set()
  for word in newlist:
    ltrs_visited.update(set(word))
  if len(ltrs_visited) >= len(letterset) and \
     (len(newlist) <= 2 or len(newlist) <= best_len_so_far):
      print(f"found: {newlist}")
      best_len_so_far = len(newlist)
      return [newlist]
  # crucial optimization: adding a word is strictly worse
  if len(newlist) >= best_len_so_far:
    return []
  lastltr = addword[-1]
  res = []
  for nextword in words_by_starting_ltr[lastltr]:
    # in theory, this provides recursion safety as well
    if ltrs_visited > set(nextword): continue
    # debugging:
    #cnt += 1
    #if cnt % 1000000 == 0 and int(time.time()) > last_time:
    #  last_time = int(time.time())
    #  print(f"{cnt} iter: words={words} + {addword} lts={''.join(sorted(ltrs_visited))} missing={''.join(sorted(list(set(letters) - ltrs_visited)))} nextword={nextword} lastltr={lastltr}")
    res += find_words(newlist, nextword)
  return res
  
words = []
for ltr in letterset:
  words += word_tree(ltr)
words_in_length_order = sorted(words, key=lambda w: len(set(w)) + (10 if (w in popular_words) else 0), reverse=True)
print(f"longest words: {[w+'('+str(len(set(w)))+')' for w in words_in_length_order][:40]}")
for word in words_in_length_order:
  words_by_starting_ltr[word[0]].append(word)
print(f"{len(words)} words: {words[0:10]} ... {words[-10:]}")

remaining_letters = letterset.copy()
finalres = []
for i, word in enumerate(words_in_length_order):
  print(f"{i} of {len(words)}: checking {word}...")
  finalres += find_words([], word)

finalres = sorted(finalres, key=lambda r: len(r))
  
print(f"finalres={finalres[0:20]}")


