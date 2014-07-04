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

"""Generate groundtruth matrix for initial pre-clustering

A pre-clustering groundtruth matrix G is K x K matrix where K is the number of
pre-clusters, G[i, j] = 1 if all items of pre-clusters i and j are in the same
reference cluster, G[i, j] = 0 if they are in two different reference clusters
and G[i, j] = -1 if at least one of pre-clusters i and j are already not
completely pure.

Usage:
  groundtruth.py <reference.txt> <pre_clustering.txt> <groundtruth.npy>
  groundtruth.py (-h | --help)
  groundtruth.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from clustering import Clustering
import numpy as np


def do_compute(reference_txt, pre_clustering_txt, groundtruth_npy):

    # load reference clusters
    reference = Clustering.load(reference_txt)

    # load hypothesis clusters
    hypothesis = Clustering.load(pre_clustering_txt)

    # number of hypothesis clusters
    nPreClusters = len(hypothesis.clusters)
    preClusters = sorted(hypothesis.clusters)

    # groundtruth[i, j] contains
    # 1 if all elements in clusters i and j are in the same cluster
    # 0 if elements in clusters i and j are not in the same cluster
    # -1 if either cluster i or j is not pure
    groundtruth = np.empty((nPreClusters, nPreClusters), dtype=int)

    # clustersRef[c] contains reference cluster for pure hypothesis cluster c
    # in case c is not pure, clustersRef[c] is None
    clustersRef = {}
    for c in preClusters:
        r = set([reference[i] for i in hypothesis.clusters[c]])
        if len(r) == 1:
            clustersRef[c] = r.pop()
        else:
            clustersRef[c] = None

    for k, ci in enumerate(preClusters):
        if clustersRef[ci] is None:
            groundtruth[ci, :] = -1
            groundtruth[:, ci] = -1
            continue
        for cj in preClusters[k:]:
            if clustersRef[cj] is not None:
                groundtruth[ci, cj] = clustersRef[ci] == clustersRef[cj]
                groundtruth[cj, ci] = groundtruth[ci, cj]

    # save groundtruth matrix
    np.save(groundtruth_npy, groundtruth)

if __name__ == '__main__':

    arguments = docopt(__doc__, version='0.1')

    reference = arguments['<reference.txt>']
    clustering = arguments['<pre_clustering.txt>']
    groundtruth = arguments['<groundtruth.npy>']
    do_compute(reference, clustering, groundtruth)
