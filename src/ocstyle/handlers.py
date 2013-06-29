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

"""Objective C parse handlers."""

from parcon import flatten

import StringIO

from ocstyle.error import Error


def drop(*_):
  """Drops output."""
  return None


def justErrors(value):
  """Check value and ensure it contains no text, only errors (or nothing)."""
  if not value:
    return None

  if not isinstance(value, list):
    value = [value]

  result = []
  for part in flatten(value):
    if part:
      if not isinstance(part, Error):
        raise Exception('Got %r when expecting only errors' % part)
      else:
        result.append(part)

  return value


def stringsAndErrors(value):
  """Aggregate both unparsed strings and errors."""
  if not value:
    return None

  if not isinstance(value, list):
    value = [value]

  result = []
  lastStringPart = None
  for part in flatten(value):
    if isinstance(part, basestring):
      lastStringPart = lastStringPart or StringIO.StringIO()
      lastStringPart.write(part)
    else:
      if lastStringPart:
        result.append(lastStringPart.getvalue())
        lastStringPart = None
      if part:
        result.append(part)
  if lastStringPart:
    result.append(lastStringPart.getvalue())
  return result
