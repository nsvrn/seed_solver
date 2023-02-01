from mnemonic import Mnemonic
import bip39 as wl
from loguru import logger
from cryptotools.BTC import Xprv
from random import shuffle
import ray
from pathlib import Path


TRIED = []
FOUND_FPATH = Path(__file__).parents[1].joinpath('match_found.txt')

def get_mlists(seed, checksum, is_shuffled):
    '''
        Returns guessed mnemonics with passed/valid checksums
    '''
    mlists = []
    guess = []

    while (guess not in TRIED):
        for idx, w in enumerate(seed):
            if w == '?':
                # set excl_list=words if you want to assume words don't repeat
                w = wl.rand_word(excl_list=[])
            guess.append(w)
        TRIED.append(guess)
                

    if is_shuffled: shuffle(guess)
    # print(words)
    
    checksum = None if checksum == '?' else checksum
    cwords = wl.get_checksum_words(guess, force=checksum)
    for cw in cwords: mlists.append(guess+[cw])
    return mlists


def _solver(target, words, checksum, passphrase, is_shuffled):
    is_found = False
    index = 1
    failed_list = []
    while(not Path(FOUND_FPATH).exists()):
        mlists = get_mlists(words, checksum, is_shuffled)
        if mlists is None or len(mlists) < 1:
            continue
        mnemo = Mnemonic('english')
        sub_index = 0
        for seed in mlists:
            seed_str = ' '.join(seed)
            print(f'{index}.{sub_index}.: {seed_str}')
            passphrase = '' if passphrase is None else passphrase
            m = Xprv.from_mnemonic(seed_str, passphrase=passphrase)
            xprv = m.encode()
            # address descriptor:
            addr = (m/84./0./0./0/0).address('P2WPKH')
            addr2 = (m/84./0./0./0/1).address('P2WPKH')
            # xpub = m.to_xpub().encode()
            print(f'{index}.{sub_index}. {addr}, {addr2}')
            sub_index += 1
            if target in [addr, addr2]:
                logger.info('*******MATCH FOUND*********')
                msg = f'mnemonic:{seed_str}, passphrase: {passphrase}, master key:{xprv}, {addr}'
                logger.info(msg)
                with open(FOUND_FPATH, "w") as text_file:
                    text_file.write(msg)
                is_found = True
                break
        if is_found: break
        index += 1

@ray.remote
def solver_m(target, words, checksum, passphrase, is_shuffled=False):
    _solver(target, words, checksum, passphrase, is_shuffled)


def solver_s(target, words, checksum, passphrase, is_shuffled=False):
    _solver(target, words, checksum, passphrase, is_shuffled)


def run_multi_process(target, seed, checksum, passphrase, is_shuffled):
    ray.init(num_cpus=6)
    ray.get([
                solver_m.remote(target, seed, checksum, passphrase, is_shuffled),
                solver_m.remote(target, seed, checksum, passphrase, is_shuffled),
                solver_m.remote(target, seed, checksum, passphrase, is_shuffled),
                solver_m.remote(target, seed, checksum, passphrase, is_shuffled),
                solver_m.remote(target, seed, checksum, passphrase, is_shuffled),
                solver_m.remote(target, seed, checksum, passphrase, is_shuffled)
            ])


def run_single_process(target, seed, checksum, passphrase, is_shuffled):
    solver_s(target, seed, checksum, passphrase, is_shuffled)
        
    

if __name__ == '__main__':
    target = 'bc1qhn3qchu9paakldtetcxml9esv3x040hxp83sj6'
    seed = ['abandon', 'abandon', 'abandon', 'abandon', 'abandon',  \
            'abandon', 'abandon', 'abandon', '?', 'abandon', 'abandon']
    checksum, passphrase = 'liquid',  None
    is_shuffled = False
    run_multi_process(target, seed, checksum, passphrase, is_shuffled)
    # run_single_process(target, seed, checksum, passphrase, is_shuffled)
    
    

