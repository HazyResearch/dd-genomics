# CONFIG
# The master configuration file for candidate extraction, distant supervision and feature
# extraction hyperparameters / configurations
import sys

if sys.version_info < (2,7):
  assert False, "Need Python version 2.7 at least"

BOOL_VALS = [('neg', False), ('pos', True)]

GENE_ACRONYMS = {
  'vals' : BOOL_VALS,
  
  ## Features
  'F' : {
    #'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  },
                     
  'HF' : {},
                     
  'SR' : { 
    'levenshtein_cutoff' : 0.2
  }
}

NON_GENE_ACRONYMS = {
  'vals' : BOOL_VALS,
  
  ## Features
  'F' : {
    #'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  },
                     
  'HF' : {},
                     
  'SR' : { 
    'levenshtein_cutoff' : 0.2,
    'short_words': { 'the', 'and', 'or', 'at', 'in', 'see', 'as', 'an', 'data', 'for', 'not', 'our', 'ie', 'to', 'eg', 'one', 'age', 'on', 'center', 'right', 'left', 'from', 'based', 'total', 'via', 'but', 'resp', 'no' } 
  }
}

PHENO_ACRONYMS = {
  'vals' : BOOL_VALS,
  
  ## Features
  'F' : {
    #'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  },
                     
  'HF' : {},
                     
  'SR' : {
    'difflib.pheno_cutoff' : 0.8,
    'short_words': { 'the', 'and', 'or', 'at', 'in', 'see', 'as', 'an', 'data', 'for', 'not', 'our', 'ie', 'to', 'eg', 'one', 'age', 'on', 'center', 'right', 'left', 'from', 'based', 'total', 'via', 'but', 'resp', 'no' } 
  }
}

### GENE
GENE = {
  'vals' : BOOL_VALS,

  ## Hard Filters (for candidate extraction)
  'HF' : {
    # Restricting the ENSEMBL mapping types we consider
    # Types: CANONICAL_SYMBOL, NONCANONICAL_SYMBOL, REFSEQ

    'ensembl-mapping-types' : ['CANONICAL_SYMBOL', 'NONCANONICAL_SYMBOL', 'ENSEMBL_ID', 'REFSEQ'],

    'min-word-len': 2
  },

  ## Supervision Rules
  'SR' : {
    # Label some P mentions based on the toks / phrases that follow
    'post-match' : {
      'pos' : [],
      'neg' : [],
      'pos-rgx' : [],
      'neg-rgx' : [r'cell(s|\slines?)']
    },

    'pre-neighbor-match' : {
      'pos' : [],
      'neg' : [],
      'pos-rgx': [],
      'neg-rgx': []
    },

    'neighbor-match': {
      'pos' : [],
      'neg' : [],
      'pos-rgx': [],
      'neg-rgx': []
    },

    'pubmed-paper-genes-true' : True,

    'complicated-gene-names-true': True,

    # all canonical and noncanonical
    'all-symbols-true': True,

    'rand-negs': True

  },

  ## Features
  'F' : {
    #'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  }
}


### VARIANT
VARIANT = {
  'vals' : BOOL_VALS,
  'HF' : {}
}

### GENE-VARIANT
GENE_VARIANT = {
  'vals' : BOOL_VALS,
  'HF' : {}
}

### PHENO
PHENO = {
  'vals' : BOOL_VALS,
  
  ## Hard Filters (for candidate extraction)
  'HF' : {
    # Maximum n-gram length to consider
    'max-len' : 8,

    # Minimum word length to consider as a non-stopword
    'min-word-len' : 3,

    # Do not extract mentions which contain these toks- e.g. split on these
    'split-list' : [',', ';'],

    # Also split on above a certain number of consecutive stopwords
    'split-max-stops' : 2,

    # Consider permuted matches to HPO words
    'permuted' : True,

    # Consider exact matches with one ommited *interior* word
    'omitted-interior' : True,

    'rand-negs' : True
  },

  ## Supervision Rules
  'SR' : {
    # Label some P mentions based on the toks / phrases that follow
    'post-match' : {
      'pos' : [],
      'neg' : [],
      'pos-rgx' : [],
      'neg-rgx' : [r'cell(s|\slines?)']
    },

    # Supervise with MeSH- optionally consider more specific terms also true (recommended)
    'mesh-supervise' : True,
    'mesh-specific-true' : True,

    # Subsample exact matches which are also english words
    'exact-english-word' : {
      'p' : 0.1
    },

    # Get random negative examples which are phrases of consecutive non-stopwords w certain
    # POS tags
    'rand-negs' : {
      'pos-tag-rgx' : r'NN.?|JJ.?'
    }
  },

  ## Features
  'F' : {
    # Add the closest verb by raw distance
    'closest-verb' : True,

    # Incorporate user keyword dictionaries via DDLIB
    'sentence-kws' : True
  }
}


### GENE-PHENO
GENE_PHENO = {
  ## Hard Filters (for candidate extraction)
  'HF' : {
    # Upper-bound the max min-dependency-path length between G and P
    'max-dep-path-dist' : 7,

    # Only consider the closest GP pairs for duplicate GP pairs
    'take-best-only-dups' : True,

    # Only consider the closest GP pairs by dep-path distance such that all G,P are covered
    'take-best-only' : True
  },

  'vals' : BOOL_VALS,

  'causation': {
    ## Supervision Rules
    'SR' : {
      # Whether to include GP pairs with no or long dep path links as neg. supervision (vs. skip)
      'bad-dep-paths' : True,

      # Subsample GP pairs where G and/or P is neg. example as neg. GP supervision
      'g-or-p-false' : {'diff' : 0.5, 'rand' : 0.01},

      # Supervise G adjacent to P as false
      'adjacent-false' : True,

      # Supervise as T/F based on phrases (exact or regex) anywhere in sentence
      'phrases-in-sent' : {
        'pos' : ['caused by mutations'],
        'neg' : ['risk', 'variance', 'patients', 'gwas', 'association study', 'reported', 'therapeutic utility', 'methylated genes', 'transcription factor', 'viral', 'virus', 'pathogen', 'families', 'possible association'],
        'pos-rgx' : [],
        'neg-rgx' : [r'rs\d+', r't?SNPs?', r'\d+(\.\d+)?\s*\%', r'\d+\s+(adult|patient|studie|subject)s']
      },

      # Supervise as T/F based on phrases (exact or regex) only between the G and P mentions
      'phrases-in-between' : False,

      # Try to find the verb connecting the G and P, and supervise based on modifiers
      # (e.g. negation, etc) of this verb
      'primary-verb-modifiers' : {
        'max-dist' : 1,
        'pos' : [],
        'neg' : ['might'],
        'pos-dep-tag' : [],
        'neg-dep-tag' : ['neg']
      },

      # Supervise GP pairs based on words (e.g. esp verbs) on the min dep path connecting them
      'dep-lemma-connectors' : {
        'pos' : ['cause'],
        'neg' : ['associate', 'correlate', 'implicate']
      },

      # Supervise GP pairs as T/F based on dependency-path neighbor lemmas of G and P
      'dep-lemma-neighbors' : {
        'max-dist' : 1,
        'pos-g' : ['cause', 'mutate', 'mutation', 'variant', 'allele'],
        'pos-p' : ['gene', 'mutation', 'mutate'],
        'neg-g' : ['express', 'expression', 'coexpression', 'coexpress', 'co-expression', 'co-express', 'overexpress', 'overexpression', 'over-expression', 'over-express', 'somatic', 'infection', 'interacts', 'regulate', 'up-regulate', 'upregulate', 'down-regulate', 'downregulate'],
        'neg-p' : []
      },

      # Label T all GP pairs in Charite dataset (and that haven't already been labeled T/F)
      'charite-all-pos' : True
    }
  },

  'association': {
    ## Hard Filters (for candidate extraction)
    'HF' : {
      # Upper-bound the max min-dependency-path length between G and P
      'max-dep-path-dist' : 7,

      # Only consider the closest GP pairs for duplicate GP pairs
      'take-best-only-dups' : True,

      # Only consider the closest GP pairs by dep-path distance such that all G,P are covered
      'take-best-only' : True
    },

    ## Supervision Rules
    'SR' : {
      # Whether to include GP pairs with no or long dep path links as neg. supervision (vs. skip)
      'bad-dep-paths' : True,

      # Subsample GP pairs where G and/or P is neg. example as neg. GP supervision
      'g-or-p-false' : {'diff' : 0.5, 'rand' : 0.01},

      # Supervise G adjacent to P as false
      'adjacent-false' : True,

      # Supervise as T/F based on phrases (exact or regex) anywhere in sentence
      'phrases-in-sent' : {
        'pos' : [],
        'neg' : [],
        'pos-rgx' : [],
        'neg-rgx' : []
      },

      # Supervise as T/F based on phrases (exact or regex) only between the G and P mentions
      'phrases-in-between' : False,

      # Try to find the verb connecting the G and P, and supervise based on modifiers
      # (e.g. negation, etc) of this verb
      'primary-verb-modifiers' : {
        'max-dist' : 1,
        'pos' : [],
        'neg' : [],
        'pos-dep-tag' : [],
        'neg-dep-tag' : []
      },

      # Supervise GP pairs based on words (e.g. esp verbs) on the min dep path connecting them
      'dep-lemma-connectors' : {
        'pos' : [],
        'neg' : []
      },

      # Supervise GP pairs as T/F based on dependency-path neighbor lemmas of G and P
      'dep-lemma-neighbors' : {
        'max-dist' : 1,
        'pos-g' : [],
        'pos-p' : [],
        'neg-g' : [],
        'neg-p' : []
      },

      # Label T all GP pairs in Charite dataset (and that haven't already been labeled T/F)
      'charite-all-pos' : True
    }

  },

  ## Features
  'F' : {}
}


### GENE-VARIANT-PHENO
GENE_VARIANT_PHENO = {
  ## Hard Filters (for candidate extraction)
  'HF' : {
    # Upper-bound the max min-dependency-path length between G and P
    'max-dep-path-dist' : 7,

    # Only consider the closest GP pairs for duplicate GP pairs
    'take-best-only-dups' : False,

    # Only consider the closest GP pairs by dep-path distance such that all G,P are covered
    'take-best-only' : False
  },

  ## Supervision Rules
  'SR' : {
    # Subsample GP pairs where G and/or P is neg. example as neg. GP supervision
    'gv-or-p-false' : {'diff' : 0.5, 'rand' : 0.01},

    # Supervise with ClinVar
    'clinvar-sup' : True
  },

  ## Features
  'F' : {}
}
