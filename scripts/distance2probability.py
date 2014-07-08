#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 Hervé BREDIN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Convert distance to probability

Usage:
  distance2probability.py train <distance_matrix> <groundtruth_matrix> <d2p_model>
  distance2probability.py apply <distance_matrix> <d2p_model> <probability_matrix>
  distance2probability.py (-h | --help)
  distance2probability.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

from docopt import docopt
from pyannote.algorithms.stats.llr import LLRIsotonicRegression
import numpy as np
import pickle


def do_train(distance_matrix, groundtruth_matrix, d2p_model):

    # load distance matrix
    x = np.load(distance_matrix)

    # load groundtruth matrix
    y = np.load(groundtruth_matrix)

    # train isotonic regression
    ir = LLRIsotonicRegression()
    ir.fit(x, y)

    # save regression
    with open(d2p_model, 'wb') as f:
        pickle.dump(ir, f)


def do_apply(distance_matrix, d2p_model, probability_matrix):

    # load distance matrix
    x = np.load(distance_matrix)

    # load regression
    with open(d2p_model, 'rb') as f:
        ir = pickle.load(f)

    # apply isotonic regression
    y = ir.apply(x)

    # save probability matrix
    np.save(probability_matrix, y)


if __name__ == '__main__':

    arguments = docopt(__doc__, version='0.1')

    if arguments['train']:
        distance_matrix = arguments['<distance_matrix>']
        groundtruth_matrix = arguments['<groundtruth_matrix>']
        d2p_model = arguments['<d2p_model>']
        do_train(distance_matrix, groundtruth_matrix, d2p_model)

    if arguments['apply']:
        distance_matrix = arguments['<distance_matrix>']
        d2p_model = arguments['<d2p_model>']
        probability_matrix = arguments['<probability_matrix>']
        do_apply(distance_matrix, d2p_model, probability_matrix)
