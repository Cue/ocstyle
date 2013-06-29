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

"""Tests for the Objective C style rules."""

from parcon import Exact

import unittest

from ocstyle import rules



class RulesTest(unittest.TestCase):
  """Tests for Objective C rules."""

  def assertMatches(self, rule, text):
    """Check if the given rule matches the given text."""
    Exact(rule).parse_string(text)


  def testDirective(self):
    """Test for preprocessor directives."""
    self.assertMatches(rules.directive, '#ifdef XYZ')
    self.assertMatches(rules.directive, '#define XYZ\\\n"a string with a backslash \\t in it"')


  def testObjCType(self):
    """Test for Objective C types."""
    self.assertMatches(rules.objcType, 'NSString *')
    self.assertMatches(rules.objcType, 'NSString*')
    self.assertMatches(rules.objcType, 'NSString **')
    self.assertMatches(rules.objcType, 'id')
    self.assertMatches(rules.objcType, 'void')
    self.assertMatches(rules.objcType, 'signed long')
    self.assertMatches(rules.objcType, 'short int')
    self.assertMatches(rules.objcType, 'unsigned long long')
    self.assertMatches(rules.objcType, 'unsigned long long int')
    self.assertMatches(rules.objcType, 'void(^)()')
    self.assertMatches(rules.objcType, 'const float(^)(id)')
    self.assertMatches(rules.objcType, 'NSArray *(^)(id, int)')
    self.assertMatches(rules.objcType, 'id<LETRenderCommandDelegate>')
    self.assertMatches(rules.objcType, 'NSObject<LETRenderCommandDelegate> *')
    self.assertMatches(rules.objcType, 'id<LETRenderCommandDelegate, NSURLConnectionDelegate>')
    self.assertMatches(rules.objcType, 'std::vector<LETRenderCommand *>::const_reverse_iterator')
    self.assertMatches(rules.objcType, 'std::vector<std::list<char>, 5>::const_reverse_iterator<potato>')


  def testSelectorPart(self):
    """Test for selector part."""
    self.assertMatches(rules.selectorPart, 'initWithKey:(NSString *)key')


  def testMethodDeclaration(self):
    """Test for the method declaration rule."""
    self.assertMatches(rules.methodDeclaration, '- (BOOL)isSet;')
    self.assertMatches(rules.methodDeclaration, '- (id)initWithKey: (NSString *)key;')
    self.assertMatches(rules.methodDeclaration, '- (NSArray *)loadWithManager:(id)manager message:(id)message;')
    self.assertMatches(rules.methodDeclaration, '- (NSArray *)loadWithManager:(id)manager\n    message:(id)message;')
    self.assertMatches(rules.methodDeclaration, '- (void)successfullyDeletedIndexWithId:(int64_t)indexId;')


  def testPropertyDeclaration(self):
    """Test for property declarations."""
    self.assertMatches(rules.propertyDeclaration, '@property BOOL shouldForceFrame;')
    self.assertMatches(rules.propertyDeclaration, '@property (readonly) SCNavigationBar * fakeBackground;')
    self.assertMatches(rules.propertyDeclaration, '@property(nonatomic, getter=isEnabled) BOOL enabled;')
    self.assertMatches(rules.propertyDeclaration, '@property (retain) IBOutlet UIImageView *backArrow;')
    self.assertMatches(rules.propertyDeclaration, '@property (copy) void (^onContentPresented)(CUTableViewItem *item);')


  def testEmptyProtocol(self):
    """Test an empty protocol."""
    self.assertMatches(rules.protocolDeclaration, '@protocol TheName\n@end')


  def testSimpleType(self):
    """Tests simple types."""
    self.assertMatches(rules.simpleType, 'long')
    self.assertMatches(rules.simpleType, 'long long')
    self.assertMatches(rules.simpleType, 'long long int')
    self.assertMatches(rules.simpleType, 'unsigned long long int')
    self.assertMatches(rules.simpleType + rules.sp(1) + rules.ivarName, 'long long _expectedLength')


  def testInstanceVariable(self):
    """Test for an instance variable."""
    self.assertMatches(rules.ivar, 'long long _expectedLength;')
    self.assertMatches(rules.ivar, 'void (^_onContentPresented)(CUTableViewItem *);')
    self.assertMatches(rules.ivar, 'NSMutableSet *_active[__CCRequestPriorityImmediately + 1];')
    self.assertMatches(rules.ivar, 'unsigned long long int _expectedLength;')


  def testInterfaceDeclaration(self):
    """Test for interface declarations."""
    self.assertMatches(rules.interface, '@interface ABC\n<DEF>\n@end')
    self.assertMatches(rules.interface, '@interface LETImageAttributes : NSObject<NSCopying>\n@end')


  def testMethod(self):
    """Test for method."""
    self.assertMatches(rules.method, '''
+ (NSString *)serverAddressWithSubdomain:(NSString *)subdomain;
{
    return FORMAT(@"%@://%@", [self serverProtocol], [self serverHostWithSubdomain:subdomain]);
}
    '''.strip())


  def testMacroCall(self):
    """Test for macro call."""
    self.assertMatches(rules.macroCall, 'CCBlockProperty(BlockURLHandler, withCheckBlock, (URLHandlingBlock));')


  def testNamespace(self):
    """Test for namespace."""
    self.assertMatches(rules.namespace, 'namespace com {}')
    self.assertMatches(rules.namespace, 'namespace com\n{\n}')
