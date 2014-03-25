"""
regexcompiler - utilities relating to regular expressions

Author: James McCracken
"""

import re


class ReplacementListCompiler(object):

    """
    Run a list of regex substitutions over a single string, in sequence.

    Arguments:
    1. A list of uncompiled regexes, where each element is a tuple in
    the form (pattern, replacement), e.g. (r"abc", r"xyz").
    """

    def __init__(self, uncompiled, caseInsensitive=None):
        self.uncompiled = uncompiled
        self.case_insensitive = caseInsensitive
        self.compiled = self._compile_list()

    def _compile_list(self):
        """
        Compiles a list or tuple of pattern/replacement tuples.

        Arguments:
        None
        """
        if self.case_insensitive is not None and self.case_insensitive:
            return [(re.compile(pattern, re.I), replacement) for
                pattern, replacement in self.uncompiled]
        else:
            return [(re.compile(pattern), replacement) for
                pattern, replacement in self.uncompiled]

    def edit(self, text):
        """
        Edit a string, list, or tuple by running the compiled regexes.

        If the argument is none of these types, it will be returned unchanged.
        Similarly, if any element within a list or tuple is not a string, that
        element will be returned unchanged: there's no type coercion.

        For each text string, each of the compiled regexes is run in turn;
        i.e. regex2 runs on the output of regex1, etc.
        - Use 'edit_once' for a version that breaks as soon as one of the
        matches is successful.

        Arguments:
        1. A string, list, or tuple

        Returns the edited version of the string, list, or tuple (whichever
        was passed as the argument)
        """
        return self._edit_engine(text, break_on_success=False)

    def edit_once(self, text):
        """
        Edit a string, list, or tuple by running the compiled regexes.

        If the argument is none of these types, it will be returned unchanged.
        Similarly, if any element within a list or tuple is not a string, that
        element will be returned unchanged: there's no type coercion.

        Each of the compiled regexes is run in turn, *until* one is
        successful, at which point the process breaks.

        Arguments:
        1. A string, list, or tuple

        Returns the edited version of the string, list, or tuple (whichever
        was passed as the argument)
        """
        return self._edit_engine(text, break_on_success=True)

    def _edit_engine(self, text, break_on_success=False):
        """
        Main substitution engine.
        """
        output = text
        if isinstance(text, (list, tuple)):
            output = []
            for string in text:
                for pattern, replacement in self.compiled:
                    string, matches = pattern.subn(replacement, string)
                    if matches and break_on_success:
                        break
                output.append(string)
            if isinstance(text, tuple):
                output = tuple(output) # convert back to a tuple
        else:
            for pattern, replacement in self.compiled:
                output, matches = pattern.subn(replacement, output)
                if matches and break_on_success:
                    break
        return output


class ReMatcher(object):

    """
    Check and capture regular expression in one pass.

    Used to support if ... elif ... else constructions without nesting.

    Initialize with the string to be checked:
        m = ReMatcher(some_string)

    Usage:
        m.match(regexp) - returns True or False if regexp is successful
        m.search(regexp) - returns True or False if regexp is successful

    'regexp' can either be a regex string or a compiled regex (i.e. the
    result of 're.compile(regexp)')

    If the match was successful, captured groups can then be retrieved
    with m.group(n), e.g. 'm.group(1)' returns the first captured group.
    """

    def __init__(self, matchstring):
        self.matchstring = matchstring
        self.rematch = None

    def search(self, regexp):
        """
        Equivalent to re.search().

        Returns True or False.
        """
        try:
            self.rematch = regexp.search(self.matchstring)
        except AttributeError:
            self.rematch = re.search(regexp, self.matchstring)
        return bool(self.rematch)

    def match(self, regexp):
        """
        Equivalent to re.match()

        Returns True or False.
        """
        try:
            self.rematch = regexp.match(self.matchstring)
        except AttributeError:
            self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, group_num):
        """
        Return any of the groups matched by the preceding regular
        expression.

        E.g. self.group(1) returns the first matched group.
        """
        if self.rematch is None:
            return None
        else:
            return self.rematch.group(group_num)
