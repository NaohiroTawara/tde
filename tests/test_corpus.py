"""test_corpus.

"""

import pytest
import numpy as np

from tde.corpus import Interval, SegmentAnnotation, Corpus, \
    interval_cmp, FragmentToken

class TestInterval(object):
    # This looks stupid, but it's good to test the wonky (in-)equalities that
    # hold for Intervals
    i1 = Interval(0., 0.5)
    i2 = Interval(0.5, 1.5)
    i3 = Interval(1.3, 1.4)

    def test_overlap(self):
        i1, i2, i3 = self.i1, self.i2, self.i3
        assert(np.isclose(i1.overlap(i2), 0.0))
        assert(np.isclose(i1.overlap(i3), 0.0))
        assert(np.isclose(i2.overlap(i3), 0.1))

    def test_overlaps(self):
        i1, i2, i3 = self.i1, self.i2, self.i3
        assert(not i1.overlaps_with(i2))
        assert(not i1.overlaps_with(i3))
        assert(i2.overlaps_with(i3))

    def test_cmp_lt_gt(self):
        i1, i2, i3 = self.i1, self.i2, self.i3
        assert(interval_cmp(i1, i2) == -1)
        assert(interval_cmp(i1, i3) == -1)
        assert(interval_cmp(i2, i1) == 1)
        assert(interval_cmp(i3, i1) == 1)

    def test_cmp_eq(self):
        i1, i2, i3 = self.i1, self.i2, self.i3
        assert(interval_cmp(i1, i1) == 0)
        assert(interval_cmp(i2, i2) == 0)
        assert(interval_cmp(i3, i3) == 0)
        assert(interval_cmp(i1, i2) != 0)
        assert(interval_cmp(i2, i3) == 0)
        assert(interval_cmp(i3, i1) != 0)

    def test_badinterval(self):
        with pytest.raises(ValueError):
            Interval(1, 0)


class TestSegmentAnnotation(object):
    tokenlist = [FragmentToken('wavfile1', Interval(0.0,0.1), 'a'),
                 FragmentToken('wavfile1', Interval(0.1,0.2), 'r'),
                 FragmentToken('wavfile1', Interval(0.2,0.3), 'm'),
                 FragmentToken('wavfile1', Interval(0.3,0.4), 's'),
                 FragmentToken('wavfile1', Interval(0.4,0.5), 'a')]
    sa = SegmentAnnotation('', tokenlist)

    def test_annotation_at_interval(self):
        assert(self.sa.annotation_at_interval(Interval(0.0, 0.5))
               == ['a', 'r', 'm', 's', 'a'])
        assert(self.sa.annotation_at_interval(Interval(0.1, 0.4))
               == ['r', 'm', 's'])
        assert(self.sa.annotation_at_interval(Interval(0.0, 0.05))
               == ['a'])
        assert(self.sa.annotation_at_interval(Interval(10, 11))
               == [])

    def test_tokens_at_interval(self):
        assert(self.sa.tokens_at_interval(Interval(0.0, 0.5))
               == self.tokenlist)
        assert(self.sa.tokens_at_interval(Interval(0.1, 0.4))
               == self.tokenlist[1:4])
        assert(self.sa.tokens_at_interval(Interval(0.0, 0.05))
               == [self.tokenlist[0]])
        assert(self.sa.tokens_at_interval(Interval(10, 11))
               == [])


class TestCorpus(object):
    file_annotations = [SegmentAnnotation('wavfile1', [
        FragmentToken('wavfile1', Interval(0.0, 0.1), 'a'),
        FragmentToken('wavfile1', Interval(0.1, 0.2), 'r'),
        FragmentToken('wavfile1', Interval(0.2, 0.3), 'm'),
        FragmentToken('wavfile1', Interval(0.3, 0.4), 's'),
        FragmentToken('wavfile1', Interval(0.4, 0.5), 'a')]),
                        SegmentAnnotation('wavfile1', [
        FragmentToken('wavfile1', Interval(0.7, 0.8), 'w'),
        FragmentToken('wavfile1', Interval(0.8, 0.9), 'o'),
        FragmentToken('wavfile1', Interval(0.9, 1.0), 'r'),
        FragmentToken('wavfile1', Interval(1.0, 1.1), 'm'),
        FragmentToken('wavfile1', Interval(1.1, 1.2), 's'),
        FragmentToken('wavfile1', Interval(1.2, 1.3), 'a')]),
                        SegmentAnnotation('wavfile2', [
        FragmentToken('wavfile2', Interval(0.1, 0.2), 'w'),
        FragmentToken('wavfile2', Interval(0.2, 0.3), 'o'),
        FragmentToken('wavfile2', Interval(0.3, 0.4), 'r'),
        FragmentToken('wavfile2', Interval(0.4, 0.5), 'd'),
        FragmentToken('wavfile2', Interval(0.5, 0.6), 's')])]

    ca = Corpus(file_annotations)

    def test_ca_intervals(self):
        exp_intervals = {'wavfile1': [Interval(0.0, 0.5), Interval(0.7, 1.3)],
                         'wavfile2': [Interval(0.1, 0.6)]}
        pred_intervals = {}
        for fname in self.ca.keys():
            intervals = [fa.interval for fa in self.ca.segment_annotations[fname]]
            pred_intervals[fname] = intervals
        assert(exp_intervals == pred_intervals)

    def test_annotation_simple(self):
        assert(self.ca.annotation('wavfile2', Interval(0.2, 0.5)) == ['o', 'r', 'd'])

    def test_annotation_complex(self):
        assert(self.ca.annotation('wavfile1', Interval(0.7, 1.2)) == ['w', 'o', 'r', 'm', 's'])