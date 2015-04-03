import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Input OMIM file.')
    parser.add_argument('outfile', help='Output TSV file name.')
    args = parser.parse_args()

    state = None
    id = None
    is_gene_or_bad_entry = False

    # OMIM text has bad line breaks; e.g.,
    # ALZHEIMER DISEASE, EARLY-ONSET, WITH CEREBRAL AMYLOID ANGIOPATHY,
    # INCLUDED;;
    #
    # 607483 THIAMINE METABOLISM DYSFUNCTION SYNDROME 2 (BIOTIN- OR THIAMINE-RESPONSIVE
    # TYPE); THMD2
    name_is_partial = False
    # there are still bad cases that we do not handle; e.g.,
    # 601039 ICHTHYOSIS-MENTAL RETARDATION SYNDROME WITH LARGE KERATOHYALIN GRANULES
    # IN THE SKIN


    names = []
    with open(args.outfile, 'w') as out:
        for line in open(args.infile):
            line = line.rstrip()
            if line == '*FIELD* NO':
                state = 'id'
            elif line == '*FIELD* TI':
                state = 'name'
            elif line.startswith('*FIELD*'):
                state = None
                name_is_partial = False
                if names:
                    if not is_gene_or_bad_entry:
                        out.write('\t'.join(['OMIM:' + id, '|'.join(names)]) + '\n')
                    names = []
                    is_gene_or_bad_entry = False
            else:
                if state == 'id':
                    id = line
                elif state == 'name':
                    if line.startswith('*') or line.startswith('+') or line.startswith('^'):
                        is_gene_or_bad_entry = True
                    name = line.strip('; ')
                    if name.find(id + ' ') in (0, 1):
                        name = name.split(id + ' ', 1)[1]
                    if name_is_partial and names:
                        names[-1] += ' ' + name
                    else:
                        names.append(name)
                    if name[-1] == ',' or name.count('(') > name.count(')'):
                        name_is_partial = True

