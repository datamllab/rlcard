#The MIT License
#
#Copyright (c) 2020 DATA Lab at Texas A&M University
#Copyright (c) 2016 OpenAI (https://openai.com)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import hashlib
import numpy as np
import os
import struct

def colorize(string, color, bold=False, highlight = False):
    """Return string surrounded by appropriate terminal color codes to
    print colorized text.  Valid colors: gray, red, green, yellow,
    blue, magenta, cyan, white, crimson
    """
    attr = []
    num = color2num[color]
    if highlight: num += 10
    attr.append(str(num))
    if bold: attr.append('1')
    attrs = ';'.join(attr)
    return '\x1b[%sm%s\x1b[0m' % (attrs, string)

def error(msg, *args):
    print(colorize('%s: %s'%('ERROR', msg % args), 'red'))

def np_random(seed=None):
    if seed is not None and not (isinstance(seed, int) and 0 <= seed):
        raise error.Error('Seed must be a non-negative integer or omitted, not {}'.format(seed))

    seed = create_seed(seed)

    rng = np.random.RandomState()
    rng.seed(_int_list_from_bigint(hash_seed(seed)))
    return rng, seed

def hash_seed(seed=None, max_bytes=8):
    """Any given evaluation is likely to have many PRNG's active at
    once. (Most commonly, because the environment is running in
    multiple processes.) There's literature indicating that having
    linear correlations between seeds of multiple PRNG's can correlate
    the outputs:

    http://blogs.unity3d.com/2015/01/07/a-primer-on-repeatable-random-numbers/
    http://stackoverflow.com/questions/1554958/how-different-do-random-seeds-need-to-be
    http://dl.acm.org/citation.cfm?id=1276928

    Thus, for sanity we hash the seeds before using them. (This scheme
    is likely not crypto-strength, but it should be good enough to get
    rid of simple correlations.)

    Args:
        seed (Optional[int]): None seeds from an operating system specific randomness source.
        max_bytes: Maximum number of bytes to use in the hashed seed.
    """
    if seed is None:
        seed = create_seed(max_bytes=max_bytes)
    _hash = hashlib.sha512(str(seed).encode('utf8')).digest()
    return _bigint_from_bytes(_hash[:max_bytes])

def create_seed(a=None, max_bytes=8):
    """Create a strong random seed. Otherwise, Python 2 would seed using
    the system time, which might be non-robust especially in the
    presence of concurrency.

    Args:
        a (Optional[int, str]): None seeds from an operating system specific randomness source.
        max_bytes: Maximum number of bytes to use in the seed.
    """
    # Adapted from https://svn.python.org/projects/python/tags/r32/Lib/random.py
    if a is None:
        a = _bigint_from_bytes(os.urandom(max_bytes))
    elif isinstance(a, str):
        a = a.encode('utf8')
        a += hashlib.sha512(a).digest()
        a = _bigint_from_bytes(a[:max_bytes])
    elif isinstance(a, int):
        a = a % 2**(8 * max_bytes)
    else:
        raise error.Error('Invalid type for seed: {} ({})'.format(type(a), a))

    return a

# TODO: don't hardcode sizeof_int here
def _bigint_from_bytes(_bytes):
    sizeof_int = 4
    padding = sizeof_int - len(_bytes) % sizeof_int
    _bytes += b'\0' * padding
    int_count = int(len(_bytes) / sizeof_int)
    unpacked = struct.unpack("{}I".format(int_count), _bytes)
    accum = 0
    for i, val in enumerate(unpacked):
        accum += 2 ** (sizeof_int * 8 * i) * val
    return accum

def _int_list_from_bigint(bigint):
    # Special case 0
    if bigint < 0:
        raise error.Error('Seed must be non-negative, not {}'.format(bigint))
    elif bigint == 0:
        return [0]

    ints = []
    while bigint > 0:
        bigint, mod = divmod(bigint, 2 ** 32)
        ints.append(mod)
    return ints
