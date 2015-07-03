# TODO:
# correlates, associated
# negation / hypothetical -> look for words modifying the closest verb to both G and P?


# Hyperparameters / switches for the candidate extraction stage
HARD_FILTERS = {
  'gene'      : {},
  'pheno'     : {},
  'genepheno' : {

    # Upper-bound the max min-dependency-path length between G and P
    'max-dep-path-dist' : 7,

    # Only consider the closest GP pairs for duplicate GP pairs
    'take-best-only-dups' : True,

    # Only consider the closest GP pairs by dependency-path distance, such that all G,P are covered
    'take-best-only' : True
  }
}


# Hyperparameters / switches for distant supervision rules 
SUPERVISION_RULES = {
  'gene'      : {},
  'pheno'     : {},
  'genepheno' : {

    # Whether to include GP pairs with no or overly-long dependency path connections as neg. supervision (or just discard)
    'bad-dep-paths' : True,

    # Whether to ignore GP pairs with a noncanonical gene
    'ignore-noncanonical' : True,

    # Whether / how much to subsample GP pairs where G and/or P is neg. example as neg. GP supervision
    'g-or-p-false' : {'diff' : 0.5, 'rand' : 0.01},

    # Supervise G adjacent to P as false
    'adjacent-false' : True,

    # Supervise as T/F based on phrases (exact or regex) anywhere in sentence
    'phrases-in-sent' : {
      'pos' : ['caused by mutations'],
      'neg' : ['risk', 'variance', 'patients', 'gwas', 'association study', 'reported', 'therapeutic utility', 'methylated genes', 'transcription factor', 'viral', 'virus', 'pathogen', 'families', 'possible association'],
      'pos-rgx' : [],
      'neg-rgx' : ['rs\d+', 't?SNPs?', '\d+(\.\d+)?\s*\%', '\d+\s+(adult|patient|studie|subject)s']
    },

    # Supervise as T/F based on phrases (exact or regex) only between the G and P mentions
    'phrases-in-between' : False,

    # Try to find the verb connecting the G and P, and supervise based on modifiers (e.g. negation, etc) of this verb
    'primary-verb-modifiers' : {
      'max-dist' : 1,
      'pos' : [],
      'neg' : ['might'],
      'pos-dep-tag' : [],
      'neg-dep-tag' : ['neg']
    },

    # Supervise GP pairs as T/F based on words (e.g. esp verbs) on the min dep path connecting them
    'dep-lemma-connectors' : {
      'pos' : ['cause'],
      'neg' : ['associate', 'correlate']
    },

    # Supervise GP pairs as T/F based on dependency-path neighbor lemmas of G and P
    'dep-lemma-neighbors' : {
      'max-dist' : 1,
      'pos-g' : ['cause', 'mutate', 'mutation', 'variant', 'allele'],
      'pos-p' : ['gene', 'mutation', 'mutate'],
      'neg-g' : ['express', 'expression', 'coexpression', 'coexpress', 'co-expression', 'co-express', 'overexpress', 'overexpression', 'over-expression', 'over-express', 'somatic', 'infection', 'interacts', 'regulate', 'up-regulate', 'upregulate', 'down-regulate', 'downregulate'],
      'neg-p' : []
    },

    # Supervise all GP pairs that occur in Charite dataset (and that haven't already been labeled T/F) as F
    'charite-all-pos' : True
  }
}


# Hyperparameters / switches for features
FEATURES = {
  'gene'      : [],
  'pheno'     : [],
  'genepheno' : []
}
