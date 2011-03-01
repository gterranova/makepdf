#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

slashable_re = re.compile(r"""([$&%#_{}])""")
quotable_re  = re.compile(r"""([~^\\])""")

def _ctag(str):
    """Quote, tag, and escape the text.

    This is a modified version of the 'ctag' function appearing in
    StructuredText.py. The differences include, 
      * it uses _split, so that it avoids escaping text in quotes or
      in math-mode.
      * it processes hrefs.
      * it escapes LaTeX special characters.
      * it doesn't try to find duplicate list items - that got moved
      into LaTeX.

    """
    if str is None: str = ''
    str = ' %s' % str			# prepend a space 
    str = quotable_re.sub('\\verb@\\1@', str)
    str = slashable_re.sub('\\\\\\1', str)
    return str


# Constants for quote education.

punct_class = r"""[!"#\$\%'()*+,-.\/:;<=>?\@\[\\\]\^_`{|}~]"""
close_class = r"""[^\ \t\r\n\[\{\(\-]"""
dec_dashes = r"""&#8211;|&#8212;"""

# Special case if the very first character is a quote
# followed by punctuation at a non-word-break. Close the quotes by brute force:
single_quote_start_re = re.compile(r"""^'(?=%s\\B)""" % (punct_class,))
double_quote_start_re = re.compile(r"""^"(?=%s\\B)""" % (punct_class,))

# Special case for double sets of quotes, e.g.:
#   <p>He said, "'Quoted' words in a larger quote."</p>
double_quote_sets_re = re.compile(r""""'(?=\w)""")
single_quote_sets_re = re.compile(r"""'"(?=\w)""")

# Special case for decade abbreviations (the '80s):
decade_abbr_re = re.compile(r"""\b'(?=\d{2}s)""")

# Get most opening double quotes:
opening_double_quotes_regex = re.compile(r"""
                (
                        \s          |   # a whitespace char, or
                        &nbsp;      |   # a non-breaking space entity, or
                        --          |   # dashes, or
                        &[mn]dash;  |   # named dash entities
                        %s          |   # or decimal entities
                        &\#x201[34];    # or hex
                )
                "                 # the quote
                (?=\w)            # followed by a word character
                """ % (dec_dashes,), re.VERBOSE)

# Double closing quotes:
closing_double_quotes_regex = re.compile(r"""
                #(%s)?   # character that indicates the quote should be closing
                "
                (?=\s)
                """ % (close_class,), re.VERBOSE)

closing_double_quotes_regex_2 = re.compile(r"""
                (%s)   # character that indicates the quote should be closing
                "
                """ % (close_class,), re.VERBOSE)

# Get most opening single quotes:
opening_single_quotes_regex = re.compile(r"""
                (
                        \s          |   # a whitespace char, or
                        &nbsp;      |   # a non-breaking space entity, or
                        --          |   # dashes, or
                        &[mn]dash;  |   # named dash entities
                        %s          |   # or decimal entities
                        &\#x201[34];    # or hex
                )
                '                 # the quote
                (?=\w)            # followed by a word character
                """ % (dec_dashes,), re.VERBOSE)

closing_single_quotes_regex = re.compile(r"""
                (%s)
                '
                (?!\s | s\b | \d)
                """ % (close_class,), re.VERBOSE)

closing_single_quotes_regex_2 = re.compile(r"""
                (%s)
                '
                (\s | s\b)
                """ % (close_class,), re.VERBOSE)

def educateQuotesLatex(s):
    """
    Parameter:  String.

    Returns:    The string, with double quotes corrected to LaTeX quotes.

    Example input:  "Isn't this fun?"
    Example output: ``Isn't this fun?'';
    """

#    s = _ctag(s)
    # Special case if the very first character is a quote
    # followed by punctuation at a non-word-break. Close the quotes by brute force:
    s = single_quote_start_re.sub("\x04", s)
    s = double_quote_start_re.sub("\x02", s)

    # Special case for double sets of quotes, e.g.:
    #   <p>He said, "'Quoted' words in a larger quote."</p>
    s = double_quote_sets_re.sub("\x01\x03", s)
    s = single_quote_sets_re.sub("\x03\x01", s)

    # Special case for decade abbreviations (the '80s):
    s = decade_abbr_re.sub("\x04", s)

    s = opening_single_quotes_regex.sub("\\1\x03", s)
    s = closing_single_quotes_regex.sub("\\1\x04", s)
    s = closing_single_quotes_regex_2.sub("\\1\x04\\2", s)

    # Any remaining single quotes should be opening ones:
    s = s.replace("'", "\x03")

    s = opening_double_quotes_regex.sub("\\1\x01", s)
    s = closing_double_quotes_regex.sub("\x02", s)
    s = closing_double_quotes_regex_2.sub("\\1\x02", s)

    # Any remaining quotes should be opening ones.
    s = s.replace('"', "\x01")

    # Finally, replace all helpers with quotes.
    return s.replace("\x01", "``").replace("\x02", "''").\
           replace("\x03", "`").replace("\x04", "'")
