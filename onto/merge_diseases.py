import argparse
from collections import defaultdict, Counter


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='Input and output directory.')
    args = parser.parse_args()

    en_words = set([x.strip().lower() for x in open('%s/../../onto/dicts/english_words.tsv' % args.dir)])

    hpo = [x.rstrip('\n').split('\t') for x in open('%s/hpo_phenotypes.tsv' % args.dir)]
    clinvar = [x.rstrip('\n').split('\t') for x in open('%s/diseases_clinvar.tsv' % args.dir)]
    deci = [x.rstrip('\n').split('\t') for x in open('%s/diseases_deci.tsv' % args.dir)]
    do = [x.rstrip('\n').split('\t', 1) for x in open('%s/diseases_do.tsv' % args.dir)]
    omim = [x.rstrip('\n').split('\t') for x in open('%s/diseases_omim.tsv' % args.dir)]
    ordo = [x.rstrip('\n').split('\t') for x in open('%s/diseases_ordo.tsv' % args.dir)]

    hpo_pairs = []
    for id, name, synonyms, related, alt_ids, is_a, mesh_term in hpo:
        if synonyms:
            name += '|' + synonyms
        hpo_pairs.append([id, name])

    diseases = defaultdict(list)
    for id, name in omim + hpo_pairs + clinvar + deci + do + ordo:
        if ' ' in id:  # for last line of clinvar
            continue

        names = set(n.strip() for n in name.lower().split('|'))
        if 'OMIM:' in id and ';' in name:
            # OMIM:102530 SPERMATOGENIC FAILURE 6; SPGF6|GLOBOZOOSPERMIA
            new_names = []
            for n in names:
                if ';' in n:
                  new_names += [x.strip() for x in n.split(';')]
                else:
                  new_names.append(n)
            names = new_names

        for n in names:
            diseases[n].append(id)

    print 'HPO + OMIM + CLINVAR + DECI + DO + ORDO'
    print '#phrases =', len(diseases)

    hist = Counter()
    for k, v in diseases.iteritems():
        hist[len(v)] += 1
    print hist

    print 'Writing to %s/all_diseases.tsv and %s/all_diseases_en.tsv' % (args.dir, args.dir)
    with open('%s/all_diseases.tsv' % args.dir, 'w') as out,\
         open('%s/all_diseases_en.tsv' % args.dir, 'w') as out_en:
        for k in sorted(diseases.keys(), key=lambda x:(len(x), x)):
            if len(k) <= 2:
                continue
            if k in en_words:
                out_en.write('%s\n' % k)
            out.write('%s\t%s\n' % (k, '|'.join(diseases[k])))
