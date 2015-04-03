import argparse

from obo_parser import parseGOOBO


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Input HPO file in OBO v1.2 format.')
    parser.add_argument('outfile', help='Output TSV file name.')
    args = parser.parse_args()

    with open(args.outfile, 'w') as out:
        for term in parseGOOBO(args.infile):
            id = term['id'][0]
            name = term['name'][0]
            alt_ids = '|'.join(term['alt_id']) if 'alt_id' in term else ''
            is_a = '|'.join(x.partition(' ')[0] for x in term['is_a']) if 'is_a' in term else ''
            synonyms = set()
            related = set()
            for s in term.get('synonym', []):
                if ' EXACT [' in s:
                    synonyms.add(s.split(' EXACT [')[0].strip('" '))
                else:
                    # RELATED, BROAD, etc.
                    related.add(s.split('" ')[0].strip('"'))
            for n in term.get('xref', []):
                if ' ' in n:
                    synonyms.add(n.partition(' ')[-1].strip('" '))
            synonyms.discard(name)
            related.discard(name)
            synonyms = '|'.join(sorted(synonyms)) if synonyms else ''
            related = '|'.join(sorted(related)) if related else ''
            out.write('\t'.join([id, name, synonyms, related, alt_ids, is_a]) + '\n')

