# This file is adapted from the tool provided with Tensorflow for
# reading the Penn Treebank dataset. The original copyright notice is
# provided below.
#
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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
#from pylearn2.scripts.tutorials.grbm_smd.make_dataset import train_pkl_path


"""Utilities for training on the Hutter Prize and PTB datasets."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os

import numpy as np


def _read_symbols(filename):
  with open(filename, "r") as f:
    return f.read()


def _read_words(filename):
  with open(filename, "r") as f:
    return f.read().decode("utf-8").replace("\n", "<eos>").split()


def _build_vocab(filename):
  data = _read_words(filename)

  counter = collections.Counter(data)
  count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

  words, _ = list(zip(*count_pairs))
  word_to_id = dict(zip(words, range(len(words))))

  return word_to_id


def _file_to_word_ids(filename, word_to_id):
  data = _read_words(filename)
  return [word_to_id[word] for word in data if word in word_to_id]


def hutter_raw_data(data_path=None, num_test_symbols=5000000):
  """Load raw data from data directory "data_path".

  The raw Hutter prize data is at:
  http://mattmahoney.net/dc/enwik8.zip

  Args:
    data_path: string path to the directory where simple-examples.tgz has
      been extracted.
    num_test_symbols: number of symbols at the end that make up the test set

  Returns:
    tuple (train_data, valid_data, test_data, unique)
    where each of the data objects can be passed to hutter_iterator.
  """

  data_path = os.path.join(data_path, "enwik8")

  raw_data = _read_symbols(data_path)
  raw_data = np.fromstring(raw_data, dtype=np.uint8)
  unique, data = np.unique(raw_data, return_inverse=True)
  train_data = data[: -2 * num_test_symbols]
  valid_data = data[-2 * num_test_symbols: -num_test_symbols]
  test_data = data[-num_test_symbols:]
  return train_data, valid_data, test_data, unique


def ptb_raw_data(data_path=None,filename='ptb.'):
  """Load PTB raw data from data directory "data_path".

  Reads PTB text files, converts strings to integer ids,
  and performs mini-batching of the inputs.

  The PTB dataset comes from Tomas Mikolov's webpage:

  http://www.fit.vutbr.cz/~imikolov/rnnlm/simple-examples.tgz

  Args:
    data_path: string path to the directory where simple-examples.tgz has
      been extracted.

  Returns:
    tuple (train_data, valid_data, test_data, vocabulary)
    where each of the data objects can be passed to PTBIterator.
  """

  train_path = os.path.join(data_path, filename+'train.txt')
  valid_path = os.path.join(data_path, filename+'valid.txt')
  test_path = os.path.join(data_path, filename+'test.txt')
  #print (train_path)

  word_to_id = _build_vocab(train_path)
  train_data = _file_to_word_ids(train_path, word_to_id)
  valid_data = _file_to_word_ids(valid_path, word_to_id)
  test_data = _file_to_word_ids(test_path, word_to_id)
  vocabulary = len(word_to_id)
#   save_name='ptb_char'
  print ('voc',vocabulary)
#   np.savez(save_name, train_data, valid_data, test_data, vocabulary)
  return train_data, valid_data, test_data, vocabulary


def data_iterator(raw_data, batch_size, num_steps):
  """Iterate on the raw Hutter prize data or the raw PTB data.

  This generates batch_size pointers into the given raw data, and allows
  minibatch iteration along these pointers.

  Args:
    raw_data: one of the raw data outputs from hutter_raw_data or ptb_raw_data.
    batch_size: int, the batch size.
    num_steps: int, the number of unrolls.

  Yields:
    Pairs of the batched data, each a matrix of shape [batch_size, num_steps].
    The second element of the tuple is the same data time-shifted to the
    right by one.

  Raises:
    ValueError: if batch_size or num_steps are too high.
  """
  raw_data = np.array(raw_data, dtype=np.int32)

  data_len = len(raw_data)
  batch_len = data_len // batch_size
  data = np.zeros([batch_size, batch_len], dtype=np.int32)
  for i in range(batch_size):
    data[i] = raw_data[batch_len * i:batch_len * (i + 1)]

  epoch_size = (batch_len - 1) // num_steps

  if epoch_size == 0:
    raise ValueError("epoch_size == 0, decrease batch_size or num_steps")

  for i in range(epoch_size):
    x = data[:, i*num_steps:(i+1)*num_steps]
    y = data[:, i*num_steps+1:(i+1)*num_steps+1]
    yield (x, y)

#ptb_raw_data('data/')
