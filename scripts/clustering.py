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


class Clustering(dict):
    """Clustering results

    # create a new clustering result from scratch

    >>> c = Clustering()
    >>> c[1] = 0   # image #1 is in cluster #0
    >>> c[2] = 0   # image #2 is in cluster #0
    >>> c[3] = 1   # image #3 is in cluster #1
    >>> c[4] = 1   # image #4 is in cluster #1
    >>> c[5] = 2   # image #5 is in cluster #2
    >>> c[6] = 2   # image #6 is in cluster #2

    # load a clustering result from text file
    # with one line per image: image_id cluster_id

    >>> path = '/vol/corpora4/mediaeval/2014/evaluation/SED_2014_Dev_Task1_Test_Submission.txt'
    >>> c = Clustering.load(path)

    # save a clustering result to text file

    >>> c.save('/tmp/result.txt')

    # c can be seen as a standard 'dict'
    # but it actually is a bi-directional 'dict'

    >>> c
    {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}
    >>> c[5]
    2
    >>> c.clusters[1]
    [3, 4]
    >>> c.clusters[c[6]] # get all images in the same cluster as image #6
    [5, 6]
    """

    def __init__(self, *args, **kwargs):
        super(Clustering, self).__init__(*args, **kwargs)
        self.clusters = {}
        for key, value in self.iteritems():
            self.clusters.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.__delitem__(key)
        super(Clustering, self).__setitem__(key, value)
        self.clusters.setdefault(value, []).append(key)

    def __delitem__(self, key):
        self.clusters.setdefault(self[key], []).remove(key)
        if self[key] in self.clusters and not self.clusters[self[key]]:
            del self.clusters[self[key]]
        super(Clustering, self).__delitem__(key)

    @classmethod
    def load(cls, path):

        clustering = cls()
        with open(path, 'r') as f:
            for line in f:
                key, value = line.strip().split()
                clustering[int(key)] = int(value)
        return clustering

    def save(self, path):
        with open(path, 'w') as f:
            for key, value in self.iteritems():
                f.write('{key:d} {value:d}\n'.format(key=key, value=value))

    def to_list(self, items):
        return [self[item] for item in items]


