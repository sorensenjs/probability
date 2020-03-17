# Copyright 2018 The TensorFlow Probability Authors.
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
# ============================================================================
"""LogNormal distribution classes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow.compat.v2 as tf

from tensorflow_probability.python.bijectors import exp as exp_bijector
from tensorflow_probability.python.distributions import logistic
from tensorflow_probability.python.distributions import transformed_distribution
from tensorflow_probability.python.internal import assert_util
from tensorflow_probability.python.internal import dtype_util
from tensorflow_probability.python.internal import tensor_util

__all__ = [
    'LogLogistic',
]


class LogLogistic(transformed_distribution.TransformedDistribution):
  """The log-logistic distribution."""

  def __init__(self,
               scale,
               concentration,
               validate_args=False,
               allow_nan_stats=True,
               name='LogLogistic'):
    """Construct a log-logistic distribution.

    The LogLogistic distribution models positive-valued random variables
    whose logarithm is logisticly distributed with mean `log(scale)` and
    scale `1/concentration`. It is constructed as the exponential
    transformation of a Logistic distribution.

    Args:
      scale: Floating-point `Tensor`;
        the scale of the log-Logistic distribution(s).
      concentration: Floating-point `Tensor`;
        the shape of the log- Logistic distribution(s).
      validate_args: Python `bool`, default `False`. Whether to validate input
        with asserts. If `validate_args` is `False`, and the inputs are
        invalid, correct behavior is not guaranteed.
      allow_nan_stats: Python `bool`, default `True`. If `False`, raise an
        exception if a statistic (e.g. mean/mode/etc...) is undefined for any
        batch member If `True`, batch members with valid parameters leading to
        undefined statistics will return NaN for this statistic.
      name: The name to give Ops created by the initializer.
    """
    parameters = dict(locals())
    with tf.name_scope(name) as name:
      dtype = dtype_util.common_dtype([scale, concentration],
                                      dtype_hint=tf.float32)
      self._scale = tensor_util.convert_nonref_to_tensor(
          scale, name='scale', dtype=dtype)
      self._concentration = tensor_util.convert_nonref_to_tensor(
          concentration, name='concentration', dtype=dtype)
      super(LogLogistic, self).__init__(
          distribution=logistic.Logistic(loc=tf.math.log(self.scale),
                                         scale=1./self.concentration),
          bijector=exp_bijector.Exp(),
          validate_args=validate_args,
          parameters=parameters,
          name=name)

  @classmethod
  def _params_event_ndims(cls):
    return dict(scale=0, concentration=0)

  @property
  def loc(self):
    """Distribution parameter for the pre-transformed mean."""
    return self.distribution.loc

  @property
  def scale(self):
    """Distribution parameter."""
    return self._scale

  @property
  def concentration(self):
    """Distribution parameter."""
    return self._concentration

  def _mean(self):
    b = 1. / self.concentration
    mean = self.scale / sinc(b)
    return tf.where(tf.greater(self.concentration, 1.), mean, np.nan)

  def _variance(self):
    b = 1. / self.concentration
    variance = self.scale ** 2 * (1. / sinc(2*b) - 1. / sinc(b)**2)
    return tf.where(tf.greater(self.concentration, 2.), variance, np.nan)

  def _mode(self):
    mode = self.scale * ((self.concentration - 1.)/(self.concentration + 1.)
                         )**(1./self.concentration)
    return tf.where(tf.greater(self.concentration, 1.), mode, np.nan)

  def _entropy(self):
    return (tf.math.log(self.scale / self.concentration) + 2.) / tf.math.log(2.)

  def _sample_control_dependencies(self, x):
    assertions = []
    if not self.validate_args:
      return assertions
    assertions.append(assert_util.assert_non_negative(
        x, message='Sample must be non-negative.'))
    return assertions

  def _parameter_control_dependencies(self, is_init):
    if is_init:
      dtype_util.assert_same_float_dtype([self.scale, self.concentration])
    if not self.validate_args:
      return []
    assertions = []
    if is_init != tensor_util.is_ref(self._scale):
      assertions.append(assert_util.assert_positive(
          self._scale, message='Argument `scale` must be positive.'))
    if is_init != tensor_util.is_ref(self._concentration):
      assertions.append(assert_util.assert_positive(
          self._concentration,
          message='Argument `concentration` must be positive.'))
    return assertions

  def _default_event_space_bijector(self):
    return exp_bijector.Exp(validate_args=self.validate_args)


def sinc(x, name=None):
  """Calculate the (normalized) sinus cardinal of x"""
  name = name or "sinc"
  with tf.name_scope(name):
    x *= np.pi
    return tf.math.sin(x)/x
