#!/usr/bin/env python
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

"""Basic Objective C style checker."""

import argparse
import os.path
import sys

import parcon

from ocstyle import rules


def check(path, maxLineLength):
  """Style checks the given path."""
  with open(path) as f:
    return checkFile(path, f, maxLineLength)


def checkFile(path, f, maxLineLength):
  """Style checks the given file object."""
  content = f.read()
  lineErrors = rules.setupLines(content, maxLineLength)
  result = parcon.Exact(rules.entireFile).parse_string(content)
  if path.endswith(('.m', '.mm')):
    result = [err for err in result if not isinstance(err, rules.Error) or not err.kind.endswith('InHeader')]
  result.extend(lineErrors)
  result.sort(key=lambda err: err.position if isinstance(err, rules.Error) else 0)
  return result


def main():
  """Main body of the script."""

  parser = argparse.ArgumentParser()
  parser.add_argument("--maxLineLength", action="store", type=int, default=120, help="Maximum line length")
  args, filenames = parser.parse_known_args()

  for filename in filenames:
    if not os.path.isdir(filename):
      print filename
      for part in check(filename, args.maxLineLength):
        if isinstance(part, rules.Error):
          print 'ERROR: %s' % part
        else:
          print 'unparsed: %r' % part
    print


if __name__ == '__main__':
  main()
