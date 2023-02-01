from numpy import loadtxt
from pathlib import Path
import numpy as np
from mnemonic import Mnemonic
from random import shuffle


def get_checksum_words(words, force=None):
    checksum_words = []
    wl = wordlist()
    mnemo = Mnemonic("english")
    if force:
        if mnemo.check(' '.join(words+[force])):
            checksum_words.append(force)
    else:
        for w in wl:
            m = words + [w]
            if mnemo.check(' '.join(m)):
                checksum_words.append(w)
    return checksum_words
    
        
def _fpath(f):
    fpath = Path(__file__).parents[0].joinpath(f)
    return fpath


def rand_word(excl_list=[], start_with=''):
    wl = wordlist(start_with)    
    words = list(set(wl) - set(excl_list))
    guess = np.random.choice(words)
    return guess
    

def wordlist(start_with=''):
    wl = []
    f = 'bip39.txt'
    wl = loadtxt(_fpath(f), dtype=str, unpack=False)
    if start_with: 
        wl = [w for w in wl if w.startswith(start_with)]
    return wl


