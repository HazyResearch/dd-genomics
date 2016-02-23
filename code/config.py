# -*- coding: utf-8 -*-
# CONFIG
# The master configuration file for candidate extraction, distant supervision and feature
# extraction hyperparameters / configurations
import sys
import copy

if sys.version_info < (2, 7):
  assert False, "Need Python version 2.7 at least"

BOOL_VALS = [('neg', False), ('pos', True)]

GENE_ACRONYMS = {
  'vals' : BOOL_VALS,

  # # Features
  'F' : {
    # 'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  },

  'HF' : {},

  'SR' : {
    'levenshtein_cutoff' : 0.2
  }
}

NON_GENE_ACRONYMS = {
  'vals' : BOOL_VALS,

  # # Features
  'F' : {
    # 'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  },

  'HF' : {},

  'SR' : {
    'levenshtein_cutoff' : 0.2,
    'short-words': { 'the', 'and', 'or', 'at', 'in', 'see', 'as', \
                    'an', 'data', 'for', 'not', 'our', 'ie', 'to', \
                    'eg', 'one', 'age', 'on', 'center', 'right', 'left', \
                    'from', 'based', 'total', 'via', 'but', 'resp', 'no' },
    'manual-pairs' : { ( 'FRAXA' ) : ['fragile X'], \
                       ('IL1', 'IL2', 'IL3', 'IL4', 'IL5', 'EL1', 'EL2', 'EL3', 'EL4', 'EL5' ) :  \
                         [ 'intracellular loop', 'extracellular loop'], \
                       ( 'GAA' ) : ['repeat', 'triplet'],  \
                       ( 'CNF' ) : ['Finnish type'],  \
                       ( 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'L1', \
                         'L2', 'L3', 'L4', 'L5', 'S1', 'S2', 'S3', 'S4', 'S5' ) : \
                         ['vertebrae', 'spine', 'fusion', 'spina'],
                       ( 'LCA10' ) : ['congenital amaurosis'], ( 'AR-JP' ) : [ 'parkinsonism' ]}
  }
}

PHENO_ACRONYMS = {
  'vals' : BOOL_VALS,

  # # Features
  'F' : {
    # 'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  },

  'HF' : {},

  'SR' : {
    'bad-pheno-names': ['MIM'],
    'difflib.pheno_cutoff' : 0.8,
    'short-words': { 'the', 'and', 'or', 'at', 'in', 
                    'see', 'as', 'an', 'data', 'for', 'not', 
                    'our', 'ie', 'to', 'eg', 'one', 'age', 
                    'on', 'center', 'right', 'left', 'from', 
                    'based', 'total', 'via', 'but', 'resp', 'no' },
    'rand-negs': True
  },


}

# ## GENE
GENE = {
  'vals' : BOOL_VALS,

  # # Hard Filters (for candidate extraction)
  'HF' : {
    # Restricting the ENSEMBL mapping types we consider
    # Types: CANONICAL_SYMBOL, NONCANONICAL_SYMBOL, REFSEQ

    'ensembl-mapping-types' : ['CANONICAL_SYMBOL', 'NONCANONICAL_SYMBOL', 'ENSEMBL_ID', 'REFSEQ'],

    'min-word-len': {
      'CANONICAL_SYMBOL' : 2,
      'NONCANONICAL_SYMBOL' : 3,
      'ENSEMBL_ID' : 3,
      'REFSEQ' : 3
    },

    'require-one-letter': True
  },

  # # Supervision Rules
  'SR' : {
    # Label some P mentions based on the toks / phrases that follow
    'bad-genes': ['ANOVA', 'MRI', 'CO2', 'gamma', 'spatial', 'tau', 'Men', \
                  'ghrelin', 'MIM', 'NHS', 'STD', 'hole', 'SDS', 'p12', 'p13', 'p53',
                  'FTDP-17', 'Elo'],

    'manual-bad' : { ( 'FRAXA' ) : ['fragile X'], \
                       ('IL1', 'IL2', 'IL3', 'IL4', 'IL5', 'EL1', 'EL2', 'EL3', 'EL4', 'EL5' ) :  \
                         [ 'intracellular loop', 'extracellular loop'], \
                       ( 'GAA' ) : ['repeat', 'triplet'],  \
                       ( 'CNF' ) : ['Finnish type'],  \
                       ( 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'L1', \
                         'L2', 'L3', 'L4', 'L5', 'S1', 'S2', 'S3', 'S4', 'S5' ) : \
                         ['vertebrae', 'spine', 'fusion', 'spina'], ( 'LCA10' ) : ['congenital amaurosis'],
                         ( 'GAN' ) : [ 'primer' ], ( 'AR-JP' ) : [ 'parkinsonism' ]},

    'post-neighbor-match' : {
      # 'pos' : ['_ mutation', 'mutation', '_ mutations', 'mutations', 'mutant', \
      #          'mutants', 'gene', 'exon', 'residue', 'residues', 'coding', \
      #          'isoform', 'isoforms', 'deletion', 'mRNA', 'homozyous'],
      'pos': ['gene'],
      'neg' : ['+', 'pathway', 'inhibitor', 'inhibitors', 'cell', 'cells', 'syndrome', 'domain'],
      'pos-rgx' : [],
      # can't copy the lt-equal sign from anywhere now, it should be down there as well
      'neg-rgx' : [r'cell(s|\slines?)', '< \d+', '<= \d+', '≥ \d+', '> \d+', '>= \d+']
    },

    'pre-neighbor-match' : {
      'pos' : ['gene', 'mutations in'],
      'neg' : ['encoding'],
      'pos-rgx': [],
      'neg-rgx': []
    },

    'neighbor-match': {
      'pos' : ['mutations'],
      'neg' : ['protein'],
      'pos-rgx': [],
      'neg-rgx': []
    },

    'phrases-in-sent': {
      'pos' : [],
      'neg' : ['serum', 'level', 'elevated', 'plasma', 'accumulate', 'accumulation', 'deposition'],
      'pos-rgx': [],
      'neg-rgx': []
    },

    'pubmed-paper-genes-true' : True,

    'complicated-gene-names-true': True,

    # all canonical and noncanonical
    'all-symbols-true': False,
    'all-canonical-true': True,

    'rand-negs': True

  },

  # # Features
  'F' : {
    # 'exclude_generic' : ['LEMMA_SEQ', 'WORD_SEQ']
  }
}


# ## VARIANT
VARIANT = {
  'vals' : BOOL_VALS,
  'HF' : {},
  'SR' : {},
  'F'  : {}
}

# ## GENE-VARIANT
GENE_VARIANT = {
  'vals' : BOOL_VALS,
  'HF' : {}
}

# ## PHENO
PHENO = {
  'vals' : BOOL_VALS,

  # # Hard Filters (for candidate extraction)
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

    'rand-negs' : True,

    'disallowed-phrases' : ['cancer', 'carcinoma']
  },

  # # Supervision Rules
  'SR' : {

    'bad-pheno-names': [],

    'bad-phenos': ['HP:0001677', 'HP:0002092', 'HP:0100753', 'HP:0002511'],

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

  # # Features
  'F' : {
    # Add the closest verb by raw distance
    'closest-verb' : True,

    # Incorporate user keyword dictionaries via DDLIB
    'sentence-kws' : True
  }
}


# ## GENE-PHENO
GENE_PHENO = {
  # # Hard Filters (for candidate extraction)
  'HF' : {
    # Upper-bound the max min-dependency-path length between G and P
    'max-dep-path-dist' : 20,

  },

  'vals' : BOOL_VALS,

  'SR': {
    # Whether to include GP pairs with no or long dep path links as neg. supervision (vs. skip)
    'bad-dep-paths' : False,

    # Subsample GP pairs where G and/or P is neg. example as neg. GP supervision
    'g-or-p-false' : {'diff' : 0, 'rand' : 0},

    # Supervise G adjacent to P as false
    'adjacent-false' : True,

    # Supervise as T/F based on phrases (exact or regex) only between the G and P mentions
    'phrases-in-between' : False,

    # Try to find the verb connecting the G and P, and supervise based on modifiers
    # (e.g. negation, etc) of this verb
    'primary-verb-modifiers' : {
      'max-dist' : 1,
      'pos' : [],
      'neg' : [  # 'might'
               ],
      'pos-dep-tag' : [],
      'neg-dep-tag' : ['neg']
    },

    # Supervise GP pairs as T/F based on dependency-path neighbor lemmas of G and P
    'dep-lemma-neighbors' : {
      'max-dist' : 1,
      # 'pos-g' : ['cause', 'mutate', 'mutation', 'variant', 'allele'],
      # 'pos-p' : ['mutation', 'mutate'],
      'pos-g' : [],
      'pos-p' : [],
      'neg-g' : ['express',
                 'expression',
                 'coexpression',
                 'coexpress',
                 'co-expression',
                 'co-express',
                 'overexpress',
                 'overexpression',
                 'over-expression',
                 'over-express',
                 'somatic',
                 'infection',
                 'interacts',
                 'regulate',
                 'up-regulate',
                 'upregulate',
                 'down-regulate',
                 'downregulate',
                 'production',
                 'product',
                 'increased',
                 'increase',
                 'increas',
                 'deficiency',
                 'exclude'
                 ],
      'neg-p' : ['without', 'except']
    },

    # Label T all GP pairs in Charite dataset (and that haven't already been labeled T/F)
    'charite-all-pos-words': ['(mutat|delet|duplicat|truncat|SNP).*caus', 'PHENO.*secondary to.*GENE', 
                              'identified.*mutations.*GENE.*PHENO'],

    # Supervise GP pairs based on words (e.g. esp verbs) on the min dep path connecting them
    'dep-lemma-connectors' : {
      'pos' : [],
      'neg' : []
    },

    'phrases-in-sent' : {
      # 'pos' : ['caused by (mutation|deletion|duplication|truncat)', 'confirmed linkage'],
      'pos' : [],
      'neg' : ['possible association',
               'to investigate',
               'could reveal',
               'to determine',
               'could not determine',
               'unclear',
               'hypothesize',
               'to evaluate',
               'plasma',
               'expression',
               'to detect',
               'mouse',
               'mice',
               'to find out',
               'inconclusive',
               'further analysis',
               'but not',
               'deficiency',
               'activity',
               'unravel',
               'fish',
               'sheep',
               'cattle',
               'dachshund',
               ],
      'pos-rgx' : [],
      # 'pos-rgx' : [],
      'neg-rgx' : [  # r'rs\d+',
                   # r't?SNPs?',
                   # r'\d+(\.\d+)?\s*\%',
                   r'PHENO.*not.*cause.*GENE',
                   r'GENE.*not.*cause.*PHENO',
                   #r'GENE.*;.*PHENO',
                   #r'PHENO.*;GENE',
                   r'\?\s*$',
                   r'to determine',
                   r'to evaluate',
                   r'to investigate',
                   r'we investigated',
                   r'we examined',
                   r'to examine',
                   r'we requested',
                   'to study',
                   'indicating that',
                   '\d+ h ',
                   r'to assess',
                   r'^\s*here we define',
                   r'whether',
                   'unlikely.*GENE.*PHENO',
                   'PHENO.*not due to.*GENE',
                   'GENE.*linked to.*PHENO',
                   'attracted.*interest',
                   'target'
                    ]
    },

    'example-sentences': {
      'pos': [],
      'neg': []
    },

    'synonyms': [set(['disease', 'disorder']), \
                 set(['mutation', 'variant', 'allele', 'polymorphism']), \
                 set(['case', 'patient', 'subject', 'family', 'boy', 'girl']), \
                 set(['present', 'display', 'characterize']), \
                 set(['nonsense', 'missense', 'frameshift']), \
                 set(['identify', 'report', 'find', 'detect']), \
                 set(['cause', 'associate', 'link', 'lead']),
                 set(['mutation', 'inhibition']), \
                 set(['recessive', 'dominant'])],

    'rescores': [(set(['cause', 'lead', 'result']), set(['associate', 'link']), -50),
                 (set(['mutation']), set(['inhibition', 'deficiency']), -50)],

  },

  # # Features
  'F' : {}
}

CAUSATION_SR = {

    'example-sentences': {
      'pos': [('onto/manual/true_causation_sentences1.tsv', 18),
              ('onto/manual/true_causation_sentences2.tsv', 27)],
      'neg': []
    },

    # Supervise as T/F based on phrases (exact or regex) anywhere in sentence
    'phrases-in-sent' : {
      'pos' : [],
      'neg' : [  # 'risk',
               'variance',
               'gwas',
               'association study',
               'possible association',
               'to investigate',
               'could reveal',
               'to determine',
               'unclear',
               'hypothesize',
               'to evaluate',
               'plasma',
               'expression',
               'to detect',
               'to find out',
               'inconclusive',
               'further analysis',
               'association',
               'associated'
               ],
      'pos-rgx' : [r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*GENE.*cause.*PHENO',
                  r'(mutat|delet|duplicat|truncat|SNP|polymorphism).*GENE.*described.*patients.*PHENO',
                  r'.*patient.*GENE.*(present with|had).*PHENO.*',
                  r'(single nucleotide polymorphisms|SNPs) in GENE.*cause.*PHENO',
                  r'(mutation|deletion).*GENE.*described.*patients.*PHENO'
                  ],
      'neg-rgx' : [],
    },
    # Supervise GP pairs based on words (e.g. esp verbs) on the min dep path connecting them
    'dep-lemma-connectors' : {
      # 'pos' : ['cause'],
      'pos': [],
      'neg' : [  # 'associate',
               # 'correlate',
               # 'implicate'
               ]
    },
}

ASSOCIATION_SR = {
    # Supervise as T/F based on phrases (exact or regex) anywhere in sentence
    'phrases-in-sent' : {
      'pos' : [],
      'neg' : [],
      # 'pos-rgx' : [r'genotype.*linked to.*PHENO', r'PHENO.*linkage to.*GENE', \
      #              r'.*GENE.*associated with.*PHENO', \
      #              '(variant|allele)?.*GENE.*(PHENO suscept|susceptibility to PHENO).*', \
      #              '(single nucleotide polymorphisms|SNPs) in GENE.*(associated with|cause).*PHENO'],
      'pos-rgx' : [],
      'neg-rgx' : [],
    }
}

def extend(map1, map2):
  rv = {}
  for item in map1:
    value = map1[item]
    if isinstance(value, dict):
      if item in map2:
        rv[item] = extend(map1[item], map2[item])
      else:
        rv[item] = map1[item]
    else:
      rv[item] = map1[item]
      if item in map2:
        for v in map2[item]:
          if v not in rv[item]:
            rv[item].append(v)
  return rv

GENE_PHENO_ASSOCIATION = copy.deepcopy(GENE_PHENO)
GENE_PHENO_CAUSATION = copy.deepcopy(GENE_PHENO)
GENE_PHENO_ASSOCIATION['SR'] = extend(GENE_PHENO_ASSOCIATION['SR'], ASSOCIATION_SR)
GENE_PHENO_CAUSATION['SR'] = extend(GENE_PHENO_CAUSATION['SR'], CAUSATION_SR)

# ## GENE-VARIANT-PHENO
GENE_VARIANT_PHENO = {
  # # Hard Filters (for candidate extraction)
  'HF' : {
    # Upper-bound the max min-dependency-path length between G and P
    'max-dep-path-dist' : 10,

    # Only consider the closest GP pairs for duplicate GP pairs
    'take-best-only-dups' : False,

    # Only consider the closest GP pairs by dep-path distance such that all G,P are covered
    'take-best-only' : False
  },

  # # Supervision Rules
  'SR' : {
    # Subsample GP pairs where G and/or P is neg. example as neg. GP supervision
    'gv-or-p-false' : {'diff' : 0, 'rand' : 0.01},

    # Supervise with ClinVar
    'clinvar-sup' : True
  },

  # # Features
  'F' : {}
}
