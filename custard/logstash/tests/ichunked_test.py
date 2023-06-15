# -*- coding:utf-8 -*-
# !/usr/bin/env python3
"""
@File    :  ichunked_test.py
@Time    :  2023/6/15 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from random import randint
import unittest

from custard.logstash.utils import ichunked


CHUNK_SIZE_SMALL = 1
CHUNK_SIZE_NORMAL = 100
CHUNK_SIZE_BIG = 750
CHUNK_ITERATIONS = 5


class IChunkedTest(unittest.TestCase):
    # ----------------------------------------------------------------------
    def _test_chunking(self, chunk_size, chunk_iterations):
        # test data
        random_extra_chunk_size = randint(0, chunk_size - 1)
        test_sequence_size = chunk_size * chunk_iterations + random_extra_chunk_size
        test_sequence = list(range(test_sequence_size))
        # keep results for assertions
        iterations = 0
        iterated_elements = []
        # test
        for sequence_subset in ichunked(test_sequence, chunk_size):
            iterations += 1
            iterated_elements.extend(sequence_subset)
            self.assertLessEqual(len(sequence_subset), chunk_size)

        expected_iterations = chunk_iterations
        if random_extra_chunk_size > 0:
            expected_iterations += 1  # add 1 because of 'random_extra_chunk_size'
        self.assertListEqual(iterated_elements, test_sequence)
        self.assertEqual(iterations, expected_iterations)

    # ----------------------------------------------------------------------
    def test_chunks_big_iterations_fixed(self):
        self._test_chunking(CHUNK_SIZE_BIG, CHUNK_ITERATIONS)

    # ----------------------------------------------------------------------
    def test_chunks_big_iterations_random(self):
        chunk_iterations = randint(3, 20)
        self._test_chunking(CHUNK_SIZE_BIG, chunk_iterations)

    # ----------------------------------------------------------------------
    def test_chunks_normal_iterations_fixed(self):
        self._test_chunking(CHUNK_SIZE_NORMAL, CHUNK_ITERATIONS)

    # ----------------------------------------------------------------------
    def test_chunks_normal_iterations_random(self):
        chunk_iterations = randint(3, 20)
        self._test_chunking(CHUNK_SIZE_NORMAL, chunk_iterations)

    # ----------------------------------------------------------------------
    def test_chunks_small_iterations_fixed(self):
        self._test_chunking(CHUNK_SIZE_SMALL, CHUNK_ITERATIONS)

    # ----------------------------------------------------------------------
    def test_chunks_small_iterations_random(self):
        chunk_iterations = randint(3, 20)
        self._test_chunking(CHUNK_SIZE_SMALL, chunk_iterations)

    # ----------------------------------------------------------------------
    def test_empty_sequence(self):
        chunk_size = 5
        test_sequence = []
        # keep results for assertions
        iterations = 0
        iterated_elements = []
        # test
        for sequence_subset in ichunked(test_sequence, chunk_size):
            iterations += 1
            iterated_elements.extend(sequence_subset)
            self.assertLessEqual(len(sequence_subset), chunk_size)

        expected_iterations = 0
        self.assertListEqual(iterated_elements, test_sequence)
        self.assertEqual(iterations, expected_iterations)


if __name__ == "__main__":
    unittest.main()
