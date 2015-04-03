import argparse

from obo_parser import parseGOOBO


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Input DiseaseOntology file in OBO v1.2 format.')
    parser.add_argument('outfile', help='Output TSV file name.')
    args = parser.parse_args()

    with open(args.outfile, 'w') as out:
        for term in parseGOOBO(args.infile):
            id = term['id'][0]
            name = term['name'][0]
            synonyms = set([name])
            for s in term.get('synonym', []):
                if ' EXACT [' in s:
                    synonyms.add(s.split(' EXACT [')[0].strip('" '))
            synonyms = '|'.join(sorted(synonyms)) if synonyms else ''
            out.write('\t'.join([id, synonyms]) + '\n')
