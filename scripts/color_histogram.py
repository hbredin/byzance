#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 CNRS (Hervé BREDIN - http://herve.niderb.fr)

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

"""
Compute color histograms for list of images.

Usage:
  color_histogram [-R <R>] [-G <G>] [-B <B>] [-H <H>] [-S <S>] [-V <V>] <input.dir> <image.txt> <output.npy>
  color_histogram -h | --help
  color_histogram --version

Options:
  -R <R> --red=<R>         Set number of bins in R channel [default: 0]
  -G <G> --green=<G>       Set number of bins in G channel [default: 0]
  -B <B> --blue=<B>        Set number of bins in B channel [default: 0]
  -H <H> --hue=<H>         Set number of bins in H channel [default: 0]
  -S <S> --saturation=<S>  Set number of bins in S channel [default: 0]
  -V <V> --value=<V>       Set number of bins in V channel [default: 0]
  -h --help                Show this screen.
  --version                Show version.
"""

from docopt import docopt
from path import path
import numpy as np
import cv2
import cv


COLOR_RANGES = {
    'B': [0, 255],  # blue
    'G': [0, 255],  # green
    'R': [0, 255],  # red
    'H': [0, 179],  # hue
    'S': [0, 255],  # saturation
    'V': [0, 255],  # value
}


class ColorHistogram(object):
    """

    Parameters
    ----------
    B, G, R, H, S, V : int, optional
        Number of bins in blue, green, red, hue, saturation and value channels.
        Setting it to 0 (default) means the corresponding channel is not used.

    Usage
    -----
    >>> extractor = ColorHistogram(H=32)
    >>> histogram = extractor('/path/to/image.jpg')

    """

    def __init__(self, H=0, S=0, V=0, R=0, G=0, B=0):
        super(ColorHistogram, self).__init__()

        # number of bins for each channel
        self.bins = {'H': H, 'S': S, 'V': V, 'R': R, 'G': G, 'B': B}

        # histogram dimension
        self._dimension = sum([v > 0 for _, v in self.bins.iteritems()])

    def get_dimension(self):
        return np.prod([v for v in self.bins.values() if v > 0])

    def __call__(self, path):

        # load image in BGR (blue-green-red) colorspace
        bgr = cv2.imread(path)
        if bgr is None:
            print 'ERROR: cannot compute histogram for %s' % path
            return np.NaN

        # get its dimension
        width, height, _ = bgr.shape

        # convert to HSV (hue-saturation-value) only if needed afterwards
        if self.bins['H'] or self.bins['S'] or self.bins['V']:
            hsv = cv2.cvtColor(bgr, cv.CV_BGR2HSV)
            # reshape to (WxH, 3)
            hsv = hsv.T.reshape((3, -1)).T

        # reshape BGR only if needed afterwards
        if self.bins['B'] or self.bins['G'] or self.bins['R']:
            # reshape to (WxH, 3)
            bgr = bgr.T.reshape((3, -1)).T

        # this numpy array will have one row per channels
        X = np.empty((width * height, self._dimension))

        # d is current row index
        d = 0

        # number of bins for each channel
        bins = []

        # variation range for each channel
        ranges = []

        # add B, G and/or R channel if requested
        for i, channel in enumerate('BGR'):
            if self.bins[channel]:
                bins.append(self.bins[channel])
                ranges.append(COLOR_RANGES[channel])
                X[:, d] = bgr[:, i]
                d = d + 1

        # add H, S and/or V channel if requested
        for i, channel in enumerate('HSV'):
            if self.bins[channel]:
                bins.append(self.bins[channel])
                ranges.append(COLOR_RANGES[channel])
                X[:, d] = hsv[:, i]
                d = d + 1

        # compute multi-dimensional histogram
        histogram, _ = np.histogramdd(X, bins=bins, range=ranges)

        # return it as a 1 x nbins array
        return histogram.reshape((1, -1)) / (width * height)


def histogram_intersection(histogram1, histogram2):
    return 1. - np.sum(np.minimum(histogram1, histogram2))


def do_it(input_dir, image_txt, output_npy,
          R=0, G=0, B=0, H=0, S=0, V=0):

    # initial color histogram extractor
    extractor = ColorHistogram(R=R, G=G, B=B, H=H, S=S, V=V)

    # load image list
    with open(image_txt, 'r') as f:
        images = [image.strip() for image in f.readlines()]

    nImages = len(images)
    nDimensions = extractor.get_dimension()
    data = np.empty((nImages, nDimensions), dtype=float)

    for i, image in enumerate(images):

        if i % 1000 == 0:
            print 'Processing image {i} / {n}'.format(i=i + 1, n=len(images))

        # 100024928 --> /path/to/input/dir/100024928.jpg
        pathToImage = path.joinpath(input_dir, image + '.jpg')
        data[i, :] = extractor(pathToImage)

    with open(output_npy, 'wb') as f:
        np.save(f, data)


if __name__ == '__main__':

    arguments = docopt(__doc__, version='Color Histogram 1.0')

    r = int(arguments['--red'])
    g = int(arguments['--green'])
    b = int(arguments['--blue'])
    h = int(arguments['--hue'])
    s = int(arguments['--saturation'])
    v = int(arguments['--value'])

    input_dir = arguments['<input.dir>']
    image_txt = arguments['<image.txt>']
    output_npy = arguments['<output.npy>']

    do_it(input_dir, image_txt, output_npy,
          R=r, G=g, B=b, H=h, S=s, V=v)

