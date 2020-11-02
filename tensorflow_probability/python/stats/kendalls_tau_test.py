# Copyright 2020 The TensorFlow Probability Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests Kendall's Tau metric."""

import random

import numpy as np
from scipy import stats

import tensorflow.compat.v2 as tf
import tensorflow_probability as tfp
from tensorflow_probability.python.internal import test_util

@test_util.test_all_tf_execution_regimes
class KendallsTauTest(test_util.TestCase):

  def test_iterative_mergesort(self):
    values = [7, 3, 9, 0, -6, 12, 54, 3, -6, 88, 1412]
    array = tf.constant(values, tf.int32)
    iperm = tf.range(len(values), dtype=tf.int32)
    exchanges, perm = tfp.stats.iterative_mergesort(array, iperm)
    self.assertEquals(exchanges, 100)
    self.assertEquals(array[perm], sorted(array))
    ordered, _ = tfp.stats.iterative_mergesort(array, perm)
    self.assertEquals(ordered, 0)

  def test_kendall_tau(self):
    x1 = [12, 2, 1, 12, 2]
    x2 = [1, 4, 7, 1, 0]
    expected = stats.kendalltau(x1, x2)[0]
    res = self.evaluate(tfp.stats.kendalls_tau(tf.constant(x1, tf.float32),
                                               tf.constant(x2, tf.float32)))
    self.assertAllClose(expected, res, atol=1e-5)


  def test_kendall_tau_float(self):
    x1 = [0.12, 0.02, 0.01, 0.12, 0.02]
    x2 = [0.1, 0.4, 0.7, 0.1, 0.0]
    expected = stats.kendalltau(x1, x2)[0]
    res = self.evaluate(tfp.stats.kendalls_tau(tf.constant(x1, tf.float32),
                                               tf.constant(x2, tf.float32)))
    self.assertAllClose(expected, res, atol=1e-5)


  def test_kendall_random_lists(self):
    left = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 7, 8, 9]
    for _ in range(10):
      right = random.sample(left, len(left))
      expected = stats.kendalltau(left, right)[0]
      res = self.evaluate(tfp.stats.kendalls_tau(
          tf.constant(left, tf.float32), tf.constant(right, tf.float32)
      ))
      self.assertAllClose(expected, res, atol=1e-5)


if __name__ == '__main__':
  tf.test.main()

