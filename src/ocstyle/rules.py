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

"""Objective C style rules."""

import functools
from parcon import AnyChar, First, Forward, Literal, Present, Regex, Translate, SignificantLiteral
from parcon import separated
from parcon import failure, match

import inspect
import re

from ocstyle.error import Error
from ocstyle.handlers import drop, justErrors, stringsAndErrors


VERBOSE = True

TAB_SIZE = 4

LINES = []

# PyLint has a very hard time with our decorator pattern.  # pylint: disable=E1120


def setupLines(content, maxLineLength):
  """Setup line position data."""
  LINES[:] = []
  pos = -1
  LINES.append(0)
  while True:
    pos = content.find('\n', pos + 1)
    if pos == -1:
      break
    LINES.append(pos)

  errors = []
  for lineNo in range(1, len(LINES)):
    lineLength = LINES[lineNo] - LINES[lineNo - 1] - 1 # Remove the \n character.
    if lineLength > maxLineLength:
      errors.append(Error(
        'LineTooLong', 'Line too long: %d chars over the %d limit' % (lineLength, maxLineLength),
        LINES[lineNo], LINES))
  return errors



class TranslateWithPosition(Translate):
  """Like Translate, but also passes position."""

  def __init__(self, parser, function, passPosition=None):
    Translate.__init__(self, parser, function)
    self._passPosition = len(inspect.getargspec(function).args) == 2 if passPosition is None else passPosition


  def parse(self, text, position, endPosition, space):
    result = self.parser.parse(text, position, endPosition, space)
    if not result:
      return failure(result.expected)
    if self._passPosition:
      translated = self.function(result.value, result.end)
    else:
      translated = self.function(result.value)
    return match(result.end, translated, result.expected)


def rule(parserPart):
  """Decorator for rule syntax."""

  def decorator(f):
    """The actual decorator."""
    return TranslateWithPosition(parserPart, f)

  return decorator


def noOut(_):
  """Outputs nothing."""
  return None



def keep(literal):
  """Shorter name for this function."""
  return SignificantLiteral(literal)


def unexpectedHandler(kind, value, pos):
  """Handle a syntactically but not stylistically valid token."""
  return Error(kind, 'Did not expect %r here' % value, pos, LINES)


def unexpected(kind, pattern):
  """Accept a pattern but mark it as a style error."""
  return -TranslateWithPosition(pattern, functools.partial(unexpectedHandler, kind), True)


def expectedHandler(kind, message, value, pos):
  """Handle a syntactically but not stylistically optional token."""
  if not value:
    return Error(kind, message, pos, LINES)


def expected(kind, message, pattern):
  """Accept a pattern or nothing but mark missing it as a style error."""
  return TranslateWithPosition(-(pattern[lambda _: True]),
                               functools.partial(expectedHandler, kind, message), True)


def sp(expectedCount):
  """A space that matches any number of spaces but stylistically expects just one."""

  def cb(value, pos):
    """The callback for the rule."""
    count = len(value)
    if expectedCount > count:
      return Error('MissingSpace', 'Expected %d, got %d' % (expectedCount, count), pos, LINES)
    elif expectedCount < count:
      return Error('ExtraSpace', 'Expected %d, got %d' % (expectedCount, count), pos, LINES)

  return TranslateWithPosition(Regex(r'[ \t]*'), cb)


xsp = unexpected('ExtraSpace', Regex(r'[ \t]+')) # Breaking naming scheme to match functions. # pylint: disable=C0103

nlOrSp = '\n' | sp(1) # Breaking naming scheme to match functions. # pylint: disable=C0103


@rule(Regex(r'[ \t]*//[^\n]*')) # Consume spaces since any number of leading spaces before a comment is ok.
def lineComment(value, pos):
  """A line comment."""
  value = value.lstrip()
  if len(value) > 2 and value[2] != ' ':
    return Error('MissingSpace', 'Should have space after //', pos, LINES)


@rule(Regex(r'#(pragma|ifdef|endif|else|if|define)(([^\\\n]+)|(\\[ \t]*\S)|(\\[ \t]*\n))*'))
def directive(_):
  """A preprocessor command, possibly multi-line."""
  return None


@rule(Regex(r'[ \t]*/\*([^*]|\*[^/])+\*/')) # Consume spaces since any number of leading spaces before a comment is ok.
def docComment(value, pos):
  """A doc comment."""
  value = value.lstrip()
  stripped = value.lstrip('/').lstrip('*')
  if stripped and stripped[0] not in (' ', '\n'):
    return Error('MissingSpace', 'Should have space after /*', pos, LINES)


@rule(lineComment | docComment | directive)
def anyPreprocessor(value):
  """Any text that is processed by the preprocessor."""
  return justErrors(value)


@rule(Regex(r'\d+(\.\d+)?'))
def number(_):
  """A number."""
  return None


@rule(Regex(r'"([^\"]|\\.)*"'))
def string(_):
  """A C string."""
  return None


@rule('@' + string)
def objcString(value):
  """An objective C string."""
  return justErrors(value)


@rule(Regex(r'<[^>]+>'))
def systemInclude(_):
  """System inclusion path."""
  return None


@rule('#' + First('import', 'include') + sp(1) + (string | systemInclude))
def inclusion(value):
  """Inclusion of another file."""
  return justErrors(value)


@rule(Regex(r'[a-zA-Z_][a-zA-Z0-9_]*'))
def identifier(value):
  """An identifier."""
  return value


@rule(identifier[1])
def className(value, position):
  """A name of a class."""
  if not value[0].isupper():
    return Error('BadClassName', 'Class names must be capitalized', position, LINES)
  return None


@rule(identifier[1])
def selectorPartName(value, position):
  """A name of a class."""
  if value[0] == '_' and value[1].islower():
    return Error('PrivateSelectorInHeader', 'Selectors starting with _ can not be in header files', position, LINES)
  if not value[0].islower():
    return Error('BadSelectorPartName', 'Selector names must not be capitalized', position, LINES)
  return None


@rule(identifier[1])
def ivarName(value, position):
  """A name of a class."""
  if not value[0] == '_' or not value[1].islower():
    return Error(
        'BadInstanceVariableName', 'Instance variable names start with _ and not be capitalized', position, LINES)
  return None


@rule(identifier[1])
def parameterName(value, position):
  """A name of a class."""
  if not value[0].islower():
    return Error('BadParameterName', 'Parameter names must not be capitalized', position, LINES)
  return None


@rule(identifier[1])
def anyIdentifier(_):
  """Matches any identifier."""
  return None


@rule(sp(1) + ':' + sp(1) + className + (',' + sp(1) + className)[...])
def baseClasses(value):
  """List of base classes."""
  return justErrors(value)


filePart = Forward() # Breaking naming scheme to match functions. # pylint: disable=C0103


@rule(Literal('@end'))
def end(_):
  """End of an interface, protocol, or implementation."""
  return None


@rule(First('long', 'short') + ' ' + xsp)
def cTypeSizeModifier(value):
  """A type size modifier."""
  return justErrors(value)


@rule(Regex(r'((signed|unsigned)\s+)?((long|short)\s+){0,2}(long|int|double|float|short)\b'))
def sizedCType(value, position):
  """A type modifier."""
  for m in re.compile(r'\s\s+').finditer(value):
    return Error('ExtraSpace', 'Extra space in type name', position + m.start(), LINES)
  return None


@rule(First('volatile', 'static', 'const') + ' ' + xsp)
def modifier(value):
  """A type modifier."""
  return justErrors(value)


@rule(xsp + '<' + xsp + anyIdentifier + (',' + ('\n' + xsp | sp(1)) + anyIdentifier)[...] + xsp + '>')
def implementedProtocols(value):
  """List of implemented protocols."""
  return justErrors(value)


objcType = Forward() # Breaking naming scheme to match functions. # pylint: disable=C0103


@rule('<' + (objcType | number) + (',' + sp(1) + (objcType | number))[...] + '>' + (Present(Literal(':')) | sp(1)))
def cppTemplateValues(value):
  """Values for a C++ template."""
  return justErrors(value)


@rule(modifier[...] + (sizedCType | anyIdentifier) + -implementedProtocols +
      (Present(Regex(r'[(),<>:]')) | sp(1)) + Literal('*')[...])
def simpleType(value): # 2 lines check is broken due to decorator wrapping. # pylint: disable=W9911
  """A type."""
  return justErrors(value)


@rule(simpleType + xsp + -parameterName)
def singleBlockParam(value):
  """Single parameter for a block."""
  return justErrors(value)


@rule('(' + -(singleBlockParam + xsp + (',' + sp(1) + singleBlockParam)[...]) + ')')
def blockParams(value):
  """Parameters to a block declaration."""
  return justErrors(value)


@rule('(^)' + xsp + blockParams)
def blockSuffix(value):
  """A suffix that, when appended to a type, makes it a block type."""
  return justErrors(value)


objcType.set(Translate(separated(simpleType + -cppTemplateValues, '::') + -blockSuffix, justErrors))


@rule(Regex(r'\[[^]]*]'))
def arrayCardinality(_):
  """Matches an array cardinality specification like [4]"""
  return None


def namedVariable(nameType):
  """Creates a pattern for a named simple or block variable."""
  return (
    (objcType + xsp + nameType + -arrayCardinality) |
    (objcType + '(^' + xsp + nameType + xsp + ')' + xsp + blockParams))


@rule(sp(4) + namedVariable(ivarName) + xsp + ';')
def ivar(value):
  """An instance variable."""
  return justErrors(value)


@rule(First('@private', '@protected', '@public', '@package'))
def ivarSection(value):
  """Section within an ivar block in an interface."""
  return justErrors(value)


@rule('{' + +(ivar | ivarSection | anyPreprocessor | (xsp + '\n')) + '}')
def ivarBlock(value):
  """Block full of ivar declarations."""
  return justErrors(value)


@rule(selectorPartName + xsp + ':' + xsp + '(' + xsp + objcType + xsp + ')' + xsp + parameterName)
def selectorPart(value):
  """A part of a selector."""
  return justErrors(value)


@rule((xsp + '\n' + +First(' ', '\t')) | sp(1))
def singleSpaceOrLineWrap(value):
  """Single space or line wrap."""
  return justErrors(value)


@rule(selectorPart + (singleSpaceOrLineWrap + selectorPart)[...])
def selectorWithParams(value):
  """Multipart selector."""
  return justErrors(value)


@rule('(' + xsp + objcType + -docComment + xsp + ')') # TODO(robbyw): More generic fix for random comments.
def methodReturnType(value):
  """A method signature return type."""
  return justErrors(value)


@rule(Regex('[-+]')[noOut] + sp(1) + methodReturnType + xsp + (selectorWithParams | selectorPartName))
def methodSignature(value):
  """A method signature."""
  return justErrors(value)


@rule(methodSignature + ';')
def methodDeclaration(value):
  """A method declaration."""
  return justErrors(value)


@rule(identifier[1])
def propertyName(value, position):
  """Checks a property name."""
  if not value[0].islower():
    return Error('BadPropertyName', 'Property names must not be capitalized', position, LINES)
  return None


@rule(Regex(r'readonly|atomic|nonatomic|copy|assign|retain|strong|weak')[drop] |
      (Regex(r'[gs]etter')[drop] + sp(1) + '=' + sp(1) + selectorPartName))
def propertyOption(value): # 2 lines check is broken due to decorator wrapping. # pylint: disable=W9911
  """Option for a property."""
  return justErrors(value)


@rule('(' + xsp + propertyOption + xsp + (',' + sp(1) + propertyOption)[...] + xsp + ')' + sp(1))
def propertyOptions(value):
  """List of options for a property."""
  return justErrors(value)


def expectedDoc(kind, message):
  """Expected documentation."""
  return expected(kind, message, docComment + xsp + '\n' + xsp)


@rule(expectedDoc('ExpectedPropertyDocInHeader', 'Property requires /** documentation */') +
      '@property' + sp(1) + -propertyOptions + -('IBOutlet ' + xsp) + namedVariable(propertyName) + xsp + ';')
def propertyDeclaration(value): # 2 lines check is broken due to decorator wrapping. # pylint: disable=W9911
  """A property declaration."""
  return justErrors(value)


@rule(First('@required', '@optional'))
def declarationSection(value):
  """Declarations sub-section in an interface or protocol."""
  return justErrors(value)


@rule(anyIdentifier + Regex(r'([^;]*);')[drop])
def macroCall(value):
  """A call to a macro."""
  return justErrors(value)


@rule(((xsp + (declarationSection | methodDeclaration | propertyDeclaration)) |
       macroCall | anyPreprocessor | (xsp + '\n'))[...])
def declarations(value): # 2 lines check is broken due to decorator wrapping. # pylint: disable=W9911
  """Declarations area of an interface."""
  return justErrors(value)


@rule(expectedDoc('ExpectedInterfaceDocInHeader', 'Interface requires /** documentation */') +
      '@interface' + sp(1) + className + -baseClasses +
      -(nlOrSp + implementedProtocols) +
      -(nlOrSp + ivarBlock) +
      declarations +
      end)
def interface(value): # 2 lines check is broken due to decorator wrapping. # pylint: disable=W9911
  """Interface declaration."""
  return stringsAndErrors(value)


@rule(expectedDoc('ExpectedProtocolDocInHeader', 'Protocol requires /** documentation */') +
      '@protocol' + sp(1) + className + -baseClasses + -(sp(1) + implementedProtocols) + xsp + '\n' +
      declarations +
      end)
def protocolDeclaration(value): # 2 lines check is broken due to decorator wrapping. # pylint: disable=W9911
  """Interface declaration."""
  return stringsAndErrors(value)


@rule('@implementation' + sp(1) + className + -(sp(1) + ivarBlock) + (filePart - end)[...] + end)
def implementation(value):
  """Implementation section."""
  return stringsAndErrors(value)


codeBlock = Forward() # Breaking naming scheme to match functions. # pylint: disable=C0103


@rule(identifier[1])
def namespaceName(value, position):
  """A name of a namespace."""
  if not value[0].islower():
    return Error('BadNamespaceName', 'Namespace name must start with a lower case letter', position, LINES)
  return None


@rule('namespace' + sp(1) + namespaceName + Regex(r'\n?\s*')[drop] + '{' + (filePart - '}')[...] + '}')
def namespace(value):
  """Namespace block."""
  return stringsAndErrors(value)


@rule(Regex('(class|struct) ')[drop] + xsp + className + -(Regex('[^{;]+')[drop] + codeBlock[drop]) + ';')
def cppClass(value):
  """A C++ class."""
  # TODO(robbyw): Better parsing here, this is very minimal.
  return justErrors(value)


@rule(identifier[1])
def localVarName(value, position):
  """A name of a class."""
  if not value[0].islower():
    return Error('BadLocalVariableName', 'Local variable must start with a lower case letter', position, LINES)
  return None


# A near-total hack to stand in for expressions.
expression = Forward() # Breaking naming scheme to match functions. # pylint: disable=C0103


@rule(Regex(r'[^();]*[^();\s]')[drop] | ('(' + -expression + ')'))
def expressionPart(value):
  """Just the errors."""
  return justErrors(value)


expression.set(Translate(+expressionPart, stringsAndErrors))


@rule(objcType + xsp + localVarName + -(sp(1) + '=' + nlOrSp + expression) + ';')
def localVar(value):
  """Just the errors."""
  return justErrors(value)


@rule(Regex('return|if|for|while|switch|case|do|else|new|delete|try|catch|finally|template|continue|break|goto'))
def keyword(_):
  """Matches keywords."""
  return None


@rule(+(Regex('[^;{}"/#]+')[drop] | string | anyPreprocessor | '/'))
def unparsedStmt(value):
  """Unparsed statement."""
  return justErrors(value)


statement = Forward() # Breaking naming scheme to match functions. # pylint: disable=C0103


@rule('if' + sp(1) + '(' + xsp + expression + xsp + ')' + ((sp(1) + codeBlock) | statement))
def ifStmt(value):
  """An if statement."""
  return justErrors(value)


@rule('for' + sp(1) + '(' + xsp + expression + xsp + ')' + ((sp(1) + codeBlock) | statement))
def forStmt(value):
  """An if statement."""
  return justErrors(value)


@rule('while' + sp(1) + '(' + xsp + expression + xsp + ')' + ((sp(1) + codeBlock) | statement))
def whileStmt(value):
  """An if statement."""
  return justErrors(value)


statement.set(Translate(
    (Regex('\s+')[drop] | ifStmt | forStmt | whileStmt | (keyword + unparsedStmt) | localVar | unparsedStmt)
     + Literal(';')[...],
    justErrors))


codeBlockBody = +( # Breaking naming scheme to match functions. # pylint: disable=C0103
    anyPreprocessor | statement | codeBlock)

codeBlock.set(Translate('{' + +codeBlockBody + '}', stringsAndErrors))


@rule(Regex('[ \t]*') + -keep('\n'))
def shouldBeNewline(result, pos):
  """Expect a newline here."""
  if not isinstance(result, tuple):
    return Error('MissingNewline', 'Should have newline after ;', pos, LINES)


@rule(-(xsp + keep(';')) + shouldBeNewline + xsp)
def shouldBeSemicolonAndNewline(result, pos):
  """A place where there should a semicolon, but compiler-wise it is optional."""
  errors = []
  if result:
    if isinstance(result, Error):
      errors.append(result)
      result = None
    else:
      errors.extend([e for e in result if isinstance(e, Error)])

  if not result:
    errors.append(Error('MissingSemicolon', 'Expected a semicolon', pos, LINES))

  return errors or None


@rule(methodSignature + shouldBeSemicolonAndNewline + codeBlock)
def method(value):
  """A method."""
  return stringsAndErrors(value)


@rule(First('@class ', '@protocol ') + xsp + anyIdentifier + xsp + ';')
def forwardDeclaration(value):
  """A forward declaration of a class."""
  return justErrors(value)


filePart.set(inclusion | interface | implementation | cppClass | namespace | '\n' | ' ' | method | methodDeclaration |
             protocolDeclaration | forwardDeclaration | string | objcString | codeBlock | anyPreprocessor | AnyChar())


@rule(+filePart)
def entireFile(value):
  """The entire file."""
  return stringsAndErrors(value)
