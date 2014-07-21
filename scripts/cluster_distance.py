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

"""Generate cosine distance matrix between cluster centroids

Usage:
  cluster_distance.py <image.txt> <features.npy> <clustering.txt> <output.npy>
  cluster_distance.py (-h | --help)
  cluster_distance.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from clustering import Clustering
import numpy as np


def do_it(image_txt, features_npy, clustering_txt, output_npy):

    # load image list
    with open(image_txt, 'r') as f:
        images = [int(line.strip()) for line in f.readlines()]
        image2index = {image: index for index, image in enumerate(images)}

    # load hypothesis clusters
    clustering = Clustering.load(clustering_txt)
    clusters = sorted(clustering.clusters)

    # load features
    features = np.load(features_npy)

    # L2 normalization (for later dot product)
    features = (features.T / np.sqrt(np.sum((features ** 2), axis=1))).T

    # find centroid image for every cluster
    centroid = {}
    for c, cluster in enumerate(clusters):

        # list of images in current cluster
        _images = clustering.clusters[cluster]

        # corresponding indices in features matrix
        _indices = [image2index[image] for image in _images]

        # compute distance matrix between
        # all images of current cluster
        _features = features[_indices, :]
        _distance = 1. - np.dot(_features, _features.T)

        # find centroid image
        i = np.argmin(np.sum(_distance, axis=0))
        centroid[cluster] = _images[i]

        print 'image %s is centroid of cluster %s' % (centroid[cluster], cluster)

    # centroid indices in features matrix
    _indices = [image2index[centroid[cluster]] for cluster in clusters]

    # compute distance matrix between all centroids
    _features = features[_indices, :]
    _distance = 1. - np.dot(_features, _features.T)

    # save distance matrix
    with open(output_npy, 'wb') as f:
        np.save(f, _distance)


if __name__ == '__main__':

    arguments = docopt(__doc__, version='0.1')

    print arguments

    image_txt = arguments['<image.txt>']
    features_npy = arguments['<features.npy>']
    clustering_txt = arguments['<clustering.txt>']
    distance_npy = arguments['<output.npy>']

    do_it(image_txt, features_npy, clustering_txt, distance_npy)
