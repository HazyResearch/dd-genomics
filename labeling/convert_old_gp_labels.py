import sys

if len(sys.argv) != 2:
    print 'Wrong number of arguments'
    print 'USAGE: ./compute_stats_helper.py $label_tsvfile $prediction_tsvfile $confidence'
    exit(1)

old_labels_fn = sys.argv[1]

with open(old_labels_fn) as f:
    for i, line in enumerate(f):
        line = line.split('\t')
        doc_id = line[0].strip()
        section_id = line[1].strip()
        sentence_id = line[2].strip()
        gene_idx = line[3].strip().strip('{}')
        pheno_idx = line[4].strip().strip('{}')
        pheno_idx = pheno_idx.split(',')
        pheno_idx_form = '-'.join(pheno_idx)
        relation_id = [doc_id, section_id, sentence_id, gene_idx, doc_id, section_id, sentence_id, pheno_idx_form]
        relation_id = '_'.join(relation_id)
        is_correct = line[5].strip()
        labeler = line[6].split('_')[0]
        print relation_id+'\t'+is_correct+'\t'+labeler