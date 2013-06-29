ocstyle
=======

Objective-C style checker

# Installation

pip install ocstyle

# Example

```objc
+(void) someMessage:(NSString*)subdomain {
    NSString *ShouldStartLowerCase;
    // ...
}
```

```$ oclint test.m
test.m
ERROR: 1:1 [1] - MissingSpace - Expected 1, got 0
ERROR: 1:8 [8] - ExtraSpace - Did not expect ' ' here
ERROR: 1:29 [29] - MissingSpace - Expected 1, got 0
ERROR: 1:41 [41] - MissingNewline - Should have newline after ;
ERROR: 1:41 [41] - MissingSemicolon - Expected a semicolon
ERROR: 2:35 [77] - BadLocalVariableName - Local variable must start with a lower case letter
```

# Goal

Make it easy to share and enforce style rules for Objective C.  The less human time we spend thinking about whitespace
and naming the better!  Also enforces the existence of basic docs.

# Related

[OCLint](http://oclint.org/) runs static analysis that helps to detect common logic errors. Use it alongside ocstyle!

# Status

This is a pretty early stage project.  We fully expect bugs and feature requests.  One notable absence is that right
now style rules are not configurable.  For example, we use the following style for messages in `.m` files:

```objc
+(void) someMessage:(NSString*)subdomain;
{
}
```

Note the inclusion of the `;` and the `{` being on the next line. We like this style because it makes it easy to copy
and paste from `.h` to `.m` and back, but maybe you have your own preferences.  We'd be very happy to accept pull
requests that make ocstyle more configurable.

# License

Apache License version 2.0

# Authors

[Cue](http://www.cueup.com)
