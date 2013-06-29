# Copyright 2012 The ocstyle Authors.
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

"""Objective C style error type."""

import bisect



class Error(object):
  """An error."""

  __slots__ = ('kind', 'position', 'message', 'lines')


  def __init__(self, kind, message, position, lines):
    self.kind = kind
    self.position = position
    self.message = message
    self.lines = lines


  def lineAndOffset(self):
    """Return the line and offset where this error occurred."""
    line = bisect.bisect_left(self.lines, self.position)
    return line, self.position - self.lines[line - 1]


  def __str__(self):
    line, offset = self.lineAndOffset()
    return '%d:%d [%d] - %s - %s' % (line, offset, self.position, self.kind, self.message)


  def __repr__(self):
    return 'Error<%s>' % self
