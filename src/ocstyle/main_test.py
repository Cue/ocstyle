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

"""Tests for the Objective C style checker."""

import os.path
import pkg_resources
import unittest

from ocstyle import main



class StyleCheckerTest(unittest.TestCase):
  """"Tests for the Objective C style checker."""

  def assertSameErrors(self, expected, actual):
    """Assert that we reported the errors that we were supposed to."""
    actual.sort()
    expected.sort()

    unexpected = []
    missing = []

    i = 0
    j = 0
    while i < len(actual) and j < len(expected):
      if actual[i] == expected[j]:
        i += 1
        j += 1
      elif actual[i] > expected[j]:
        missing.append(expected[j])
        j += 1
      else:
        unexpected.append(actual[i])
        i += 1

    unexpected.extend(actual[i:])
    missing.extend(expected[j:])

    messages = []
    for item in unexpected:
      messages.append('Got unexpected error "%s" at line %d' % item)

    for item in missing:
      messages.append('Expected error but was not reported: "%s" at line %d' % item)

    if messages:
      self.fail('\n'.join(messages))


  def testSampleFiles(self):
    """Iterates through sample files and verifies if the expected style errors are reported."""
    files = [filename for filename in pkg_resources.resource_listdir('ocstyle', 'testdata')
             if filename.endswith(('.h', '.m', 'mm'))]
    self.assertNotEquals([], files)
    for filename in files:
      print filename # OK to print in a test. # pylint: disable=W9914

      errors = []
      badParse = []
      with pkg_resources.resource_stream('ocstyle', os.path.join('testdata', filename)) as f:
        result = main.checkFile(filename, f, 120)
      for part in result:
        if isinstance(part, basestring):
          badParse.append(part)
        else:
          errors.append((part.kind, part.lineAndOffset()[0]))

      if badParse:
        self.fail('Failed to parse : %r' % badParse)

      expected = []
      with pkg_resources.resource_stream('ocstyle', os.path.join('testdata', filename)) as f:
        lineNumber = 1
        for line in f:
          _, _, expect = line.partition('// EXPECT')
          if expect:
            offset, _, errorList = expect.partition(':')
            if offset:
              if offset[0] == '+':
                offset = int(offset[1:])
              else:
                offset = - int(offset[1:])
            else:
              offset = 0
            for error in errorList.split(','):
              expected.append((error.strip(), lineNumber + offset))
              error.strip()
          lineNumber += 1

      self.assertSameErrors(expected, errors)
