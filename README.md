ocstyle
=======

Objective-C style checker

# Installation

```
pip install ocstyle
```

# Example

If you have a file called `test.m` like this:

```objc
+(void) someMessage:(NSString*)subdomain {
    NSString *ShouldStartLowerCase;
    // ...
}
```

You can check style in it like this:

```
$ ocstyle test.m
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
and naming the better!  Also enforces the existence of basic documentation.

At [Cue](http://www.cueup.com) we use this as a
[git pre-commit hook](http://git-scm.com/book/en/Customizing-Git-Git-Hooks).
This way we ensure everyone maintains a consistent coding style with a minimum of effort.

# Related

[OCLint](http://oclint.org/) runs static analysis that helps to detect common logic errors. Use it alongside ocstyle!

# Status

This is a pretty early stage project.  We fully expect bugs and feature requests!

One notable absence is that right now style rules are not configurable.  For example, we use the following style
for message implementations:

```objc
+(void) someMessage:(NSString*)subdomain;
{
}
```

Note the inclusion of the `;` and the `{` being on the next line. We like this style because it makes it easy to copy
and paste from `.h` to `.m` and back, but maybe you have your own preferences.  We'd be very happy to accept pull
requests that make ocstyle more configurable.

For the motivated pull requesters out there, other notable TODOs include:

* Allow inline disabling of specific errors.

* Fix various whitespace false negatives noted in test files


# Links

ocstyle is built using [parcon](http://www.opengroove.org/parcon/parcon-tutorial.html), a really nice parser
generator library for Python.

Other linters and style checkers we use at Cue include:

* Objective C: [OCLint](http://oclint.org/)

* Java: [checkstyle](http://checkstyle.sourceforge.net/)

* JavaScript: [Closure linter](https://developers.google.com/closure/utilities/)

* Python: [pylint][http://www.logilab.org/857]


# License

Apache License version 2.0

# Authors

[Cue](http://www.cueup.com)
