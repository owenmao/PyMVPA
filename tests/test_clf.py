#emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
#ex: set sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Unit tests for PyMVPA basic Classifiers"""

import unittest

import numpy as N

from mvpa.datasets.dataset import Dataset
from mvpa.datasets.maskmapper import MaskMapper

from mvpa.clfs.classifier import Classifier, BoostedClassifier, \
     BinaryClassifierDecorator, BoostedMulticlassClassifier, \
     MappedClassifier

from copy import deepcopy

class SameSignClassifier(Classifier):
    """Dummy classifier which reports +1 class if both features have
    the same sign, -1 otherwise"""

    def __init__(self):
        Classifier.__init__(self)
    def train(self, data):
        # we don't need that ;-)
        pass
    def predict(self, data):
        datalen = len(data)
        values = []
        for d in data:
            values.append(2*int( (d[0]>=0) == (d[1]>=0) )-1)
        self["predictions"] = values
        return values


class Less1Classifier(SameSignClassifier):
    """Dummy classifier which reports +1 class if abs value of max less than 1"""
    def predict(self, data):
        datalen = len(data)
        values = []
        for d in data:
            values.append(2*int(max(d)<=1)-1)
        self["predictions"] = values
        return values


class ClassifiersTests(unittest.TestCase):

    def setUp(self):
        self.clf_sign = SameSignClassifier()
        self.clf_less1 = Less1Classifier()

        # simple binary dataset
        self.data_bin_1 = ([[0,0],[-10,-1],[1,0.1],[1,-1],[-1,1]],
                           [1, 1, 1, -1, -1])

    def testDummy(self):
        clf = SameSignClassifier()
        clf.train(None)
        self.failUnlessEqual(clf.predict(self.data_bin_1[0]), self.data_bin_1[1])

    def testBoosted(self):
        # XXXXXXX
        # silly test if we get the same result with boosted as with a single one
        bclf = BoostedClassifier(clfs=[deepcopy(self.clf_sign),
                                       deepcopy(self.clf_sign)])
        self.failUnlessEqual(bclf.predict(self.data_bin_1[0]),
                             self.data_bin_1[1],
                             msg="Boosted classifier should work")
        self.failUnlessEqual(bclf.predict(self.data_bin_1[0]),
                             self.clf_sign.predict(self.data_bin_1[0]),
                             msg="Boosted classifier should have the same as regular")


    def testBinaryDecorator(self):
        ds = Dataset(samples=[ [0,0], [0,1], [1,100], [-1,0], [-1,-3], [ 0,-10] ],
                     labels=[ 'sp', 'sp', 'sp', 'dn', 'sn', 'dp'])
        testdata = [ [0,0], [10,10], [-10, -1], [0.1, -0.1], [-0.2, 0.2] ]
        # labels [s]ame/[d]ifferent (sign), and [p]ositive/[n]egative first element

        clf = SameSignClassifier()
        # lets create classifier to descriminate only between same/different,
        # which is a primary task of SameSignClassifier
        bclf1 = BinaryClassifierDecorator(clf=clf,
                                          poslabels=['sp', 'sn'],
                                          neglabels=['dp', 'dn'])
        self.failUnless(bclf1.predict(testdata) ==
                        [['sp', 'sn'], ['sp', 'sn'], ['sp', 'sn'],
                         ['dn', 'dp'], ['dn', 'dp']])

        # check by selecting just 
        #self. fail

    def testMappedDecorator(self):
        testdata3 = N.array([ [0,0,-1], [1,0,1], [-1,-1, 1], [-1,0,1], [1, -1, 1] ])
        res110 = [1, 1, 1, -1, -1]
        res101 = [-1, 1, -1, -1, 1]
        res011 = [-1, 1, -1, 1, -1]

        clf110 = MappedClassifier(clf=self.clf_sign, mapper=MaskMapper(N.array([1,1,0])))
        clf101 = MappedClassifier(clf=self.clf_sign, mapper=MaskMapper(N.array([1,0,1])))
        clf011 = MappedClassifier(clf=self.clf_sign, mapper=MaskMapper(N.array([0,1,1])))

        self.failUnlessEqual(clf110.predict(testdata3), res110)
        self.failUnlessEqual(clf101.predict(testdata3), res101)
        self.failUnlessEqual(clf011.predict(testdata3), res011)

def suite():
    return unittest.makeSuite(ClassifiersTests)


if __name__ == '__main__':
    import test_runner
