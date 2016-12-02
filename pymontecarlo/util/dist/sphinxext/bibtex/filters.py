#!/usr/bin/env python
"""
================================================================================
:mod:`filters` -- Additional filters to Jinja to format title, names, etc.
================================================================================

.. module:: filters
   :synopsis: Additional filters to Jinja to format title, names, etc.

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from pyparsing import \
    Word, nestedExpr, originalTextFor, removeQuotes, alphas, nums

# Third party modules.

# Local modules.

# Globals and constants variables.
PREPOSITIONS = ['a', "an", 'abaft', 'aboard', 'about', 'above', 'absent', 'across',
                'afore', 'after', 'against', 'along', 'alongside', 'amid', 'amidst',
                'among', 'amongst', 'apropos', 'around', 'as', 'aside', 'astride',
                'at', 'athwart', 'atop', 'barring', 'before', 'behind', 'below',
                'beneath', 'beside', 'besides', 'between', 'betwixt', 'beyond', 'but',
                'by', 'circa', 'concerning', 'despite', 'down', 'during', 'except',
                'excluding', 'failing', 'following', 'for', 'from', 'given', 'in',
                'including', 'inside', 'into', 'like', 'mid', 'midst', 'minus', 'near',
                'next', 'notwithstanding', 'of', 'off', 'on', 'onto', 'opposite',
                'out', 'outside', 'over', 'pace', 'past', 'per', 'plus', 'pro', 'qua',
                'regarding', 'round', 'sans', 'save', 'since', 'than', 'through',
                'throughout', 'till', 'times', 'to', 'toward', 'towards', 'under',
                'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'vs.',
                'via', 'vice', 'with', 'within', 'without', 'worth']
CONJUNTIONS = ['for', 'and', 'nor', 'but', 'or', 'yet', 'so',
               'either', 'not', 'neither', 'both', 'whether',
               'after', 'although', 'as', 'much', 'soon', 'because', 'before',
               'if', 'in', 'that', 'lest', 'since', 'so', 'than', 'that',
               'though', 'unless', 'until', 'when', 'whenever', 'where',
               'wherever', 'whether', 'while']
PRONONS = ['me', 'myself', 'mine', 'my', 'mine', 'we', 'us', 'ourselves',
           'ourself', 'ours', 'our', 'you', 'yourself', 'yours', 'your',
           'yourselves', 'yours', 'your',
           'he', 'him', 'himself', 'his', 'her', 'herself', 'hers'
           'it', 'itself', 'its', 'one', 'oneself',
           'they', 'them', 'themself', 'themselves', 'theirs', 'their']
ARTICLES = ['the', 'a', 'an']
NUMBERS = ["zero", "oh", "zip", "zilch", "nada", "bupkis", "one", "two",
           "three", "four", "five", "six", "seven", "eight", "nine", "ten",
           "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
           "seventeen", "eighteen", "nineteen", "ten", "twenty", "thirty",
           "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "thousand",
           "million", "billion", "trillion", "quadrillion", "quintillion"]
COPULA = ["be", "am", "is", "are", "being", "was", "were", "been"]

CLOSED_WORD = set(PREPOSITIONS) | set(CONJUNTIONS) | set(PRONONS) | \
              set(ARTICLES) | set(NUMBERS) | set(COPULA)

bibtexChars = alphas + nums + "\\\\.-':,"
bracedWord = originalTextFor(nestedExpr("{", "}"))
bracedWord.addParseAction(removeQuotes)
WORDS = Word(bibtexChars) | bracedWord('braced')

def caps(text):
    """
    Capitalizes the first letter of the text and keeps the rest of the text
    intact.
    """
    if text:
        return text[0].upper() + text[1:]
    return ''

def abbrev(text, sep=' '):
    """
    Abbreviates a text.
    
    **Examples**:
    
        * Charles Louis -> C. L.
        * Charles Louis -> C.L. (with ``sep = ''``)
        * C. Louis -> C. L.
        * Charles Louis-Xavier -> C. L.-X.
        * Charles Louis-Xavier Joseph de la Vall\'ee Poussin -> C. L.-X. J. V. P.
    """
    abbrevs = []

    for word, _start, _end in WORDS.scanString(text):
        if not word.braced:
            doublebarrels = []

            for hypen in word[0].split('-'):
                first_letter = hypen[0]
                if first_letter.isupper():
                    doublebarrels.append("%s." % first_letter)

            if doublebarrels:
                abbrevs.append('-'.join(doublebarrels))
        else: # skip braced words
            abbrevs.append(word[0])

    return sep.join(abbrevs)

def title_case(text):
    """
    Capitalizes of all words, except for articles, prepositions, conjunctions, 
    and forms of to be.
    
    Reference: Wikipedia - Letter case
    """
    title = []

    for word, _start, _end in WORDS.scanString(text):
        if not word.braced:
            if word[0] not in CLOSED_WORD:
                title.append(caps(word[0]))
            else:
                title.append(word[0])
        else:
            title.append(word[0])

    return caps(' '.join(title))

def sentence_case(text):
    """
    Sentence case - Capitalization of only the first word.
    
    Reference: Wikipedia - Letter case
    """
    # split words
    parts = []
    nbraces = 0
    part = ''
    for c in text:
        if c == '{': nbraces += 1
        if c == '}': nbraces -= 1

        if c == ' ' and nbraces == 0:
            parts.append(part)
            part = ''

        part += c

    parts.append(part)

    # remove leading and trailing whitespaces
    parts = [part.strip() for part in parts]

    # ignore braces
    out = ' '
    for part in parts:
        if part.startswith('{') and part.endswith('}'):
            out += part[1:-1]
        else:
            out += part.lower()

        out += ' '

    # capitalize after colon and dash
    out = ': '.join([caps(part.strip()) for part in out.split(":")])
    out = ' --- '.join([caps(part.strip()) for part in out.split("---")])

    return out

def remove_empty(items):
    """
    Removes empty items for the list.
    """
    return [item for item in items if item]
