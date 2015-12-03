######################################################################################
#  LATTICE - MEMEX plugins for latticelib
#
#  latticelib is an extraction framework to allow quickly building extractors by
#  specifying minimal target-specific code (candidate generation patterns and
#  supervision rules). It has a set of pre-built featurization code that covers
#  a lot of Memex flag extractors. The goal is to make it more general,
#  powerful, fast to run and easy to use.
#
#  This file contains Memex-specific components for latticelib.
#
#  For sample usage, see:
#      udf/util/test/latticelib/module.py
#      udf/extract_underage.py
#
######################################################################################

# Default dictionaries tailored for Memex. Will function in addition to the
# one in latticelib
default_dicts = {
    'short_words': [
        'the', 
        'and', 
        'or', 
        'at', 
        'in', 
        'see', 
        'as', 
        'an', 
        'data', 
        'for', 
        'not', 
        'our', 
        'ie', 
        'to', 
        'eg', 
        'one', 
        'age', 
        'on', 
        'center', 
        'right', 
        'left', 
        'from', 
        'based', 
        'total', 
        'via', 
        'but', 
        'resp', 
        'no',
    ],
    'intensifiers': [
        'very',
        'really',
        'extremely',
        'exceptionally',
        'incredibly',
        'unusually',
        'remarkably',
        'particularly',
        'absolutely',
        'completely',
        'quite',
        'definitely',
        'too',
    ],
    'pos_certainty': [
        'likely',
        'possibly',
        'definitely',
        'absolutely',
        'certainly',
    ],
    'modal': [
        'will',
        'would',
        'may',
        'might',
    ],
    'mutation': [
      'mutation',
      'variant',
      'allele',
      'deletion',
      'duplication',
      'truncation',
    ],
    'levels': [
      'serum',
      'level',
      'elevated',
      'plasma',
    ]
    'expression': [
        'express',
        'expression',
        'coexpression',
        'coexpress',
        'co-expression',
        'co-express',
        'overexpress',
        'overexpression',
        'over-expression',
        'over-express',
        'production',
        'product',
        'increased',
        'increase',
        'increas',
    ]
}
