#! /usr/bin/env python3
#
# This script takes approved symbols, alternate symbols, and approved long names
# from the three dictionaries of genes we currently have, and tries to obtain a
# single dictionary that contains the union of the information available.
# 
# The output is a TSV file where the first column is the approved symbols, the
# second column is a list of alternate symbols (separated by '|'), and the
# third is a list of possible long names (separated by '|').
#

import sys

from helper.easierlife import BASE_DIR

HUGO_alternate_symbolS_FILE = BASE_DIR + "/dicts/hugo_synonyms.tsv"
HGNC_APPROVED_NAMES_FILE = BASE_DIR + "/dicts/HGNC_approved_names.txt"
GENES_PHARM_FILE = BASE_DIR + "/dicts/genes_pharm.tsv"

alternate_symbols = dict()
alternate_symbols_inverted = dict()
long_names = dict()

with open(HUGO_alternate_symbolS_FILE, 'rt') as hugo_file:
    for line in hugo_file:
        tokens = line.rstrip().split("\t")
        symbol = tokens[0]
        if symbol not in alternate_symbols:
            alternate_symbols[symbol] = set()
        alternate_symbols[symbol].add(symbol)
        alternate_symbols_inverted[symbol] = set([symbol,])
        if len(tokens) > 1:
            for alternate_symbol in tokens[1].split(","):
                if alternate_symbol not in alternate_symbols:
                    alternate_symbols[alternate_symbol] = set()
                alternate_symbols[alternate_symbol].add(symbol)
                alternate_symbols_inverted[symbol].add(alternate_symbol)
        long_names[symbol] = set()

with open(HGNC_APPROVED_NAMES_FILE, 'rt') as hgnc_file:
    for line in hgnc_file:
        tokens = line.rstrip().split("\t")
        symbol = tokens[0]
        if symbol.endswith("withdrawn"):
            # TODO XXX (Matteo): or should we take care of withdrawn symbols?
            continue
        #sys.stderr.write("symbol:{}\n".format(symbol))
        hgnc_alternate_symbols = set([x.strip() for x in tokens[1].split(",")])
        if symbol in alternate_symbols and symbol in alternate_symbols[symbol]:
            # the symbol is a 'main' symbol from hugo, use it as it is.
            pass
        elif symbol in alternate_symbols and symbol not in alternate_symbols[symbol]:
            # the symbol is not a main symbol from hugo, use one of its main
            # symbols (the first when the set is converted to list) as main symbol.
            # XXX (Matteo) There's no reason to choose the "first", we could
            # choose any.
            new_symbol = list(alternate_symbols[symbol])[0]
            hgnc_alternate_symbols.discard(new_symbol)
            hgnc_alternate_symbols.add(symbol)
            symbol = new_symbol
        elif symbol not in alternate_symbols:
            # the symbol did not appear at all in hugo
            found_new_symbol = False
            for candidate in hgnc_alternate_symbols:
                if candidate in alternate_symbols and candidate in alternate_symbols[candidate]:
                    # we found a symbol that is an alternate symbol in hgnc and
                    # a main symbol in hugo. Elect it as main symbol for this entry
                    new_symbol = candidate
                    hgnc_alternate_symbols.discard(new_symbol)
                    hgnc_alternate_symbols.add(symbol)
                    symbol = new_symbol
                    found_new_symbol = True
                    break
            if not found_new_symbol:
                for candidate in hgnc_alternate_symbols:
                    if candidate in alternate_symbols and \
                            candidate not in alternate_symbols[candidate]:
                        # we found a symbol that is an alternate symbol in hgnc
                        # and an alternate symbol in hugo. Elect the 'first' main
                        # symbol for this candidate as main symbol for this
                        # entry
                        new_symbol = list(alternate_symbols[candidate])[0]
                        hgnc_alternate_symbols.discard(new_symbol)
                        hgnc_alternate_symbols.add(symbol)
                        symbol = new_symbol
                        found_new_symbol = True
                        break
            if not found_new_symbol:
                # the symbol is not in hugo at all and none of its alternate in
                # hgnc appears in hugo either. This is a completely new symbol
                alternate_symbols[symbol] = set([symbol,])
                alternate_symbols_inverted[symbol] = set([symbol,])
                long_names[symbol] = set()
        else:
            sys.stderr.write("WE SHOULDN'T BE HERE\n")
        for alternate_symbol in hgnc_alternate_symbols:
            if len(alternate_symbol) == 0:
                continue
            if alternate_symbol not in alternate_symbols:
                alternate_symbols[alternate_symbol] = set([symbol,])
                alternate_symbols_inverted[symbol].add(alternate_symbol)
        # TODO XXX (Matteo) the format of the long names in hgnc is weird
        long_names[symbol].add(tokens[2])

with open(GENES_PHARM_FILE, 'rt') as pharm_file:
    ## skip header
    pharm_file.readline()
    for line in pharm_file:
        tokens = line.rstrip().split("\t")
        symbol = tokens[4]
        if symbol.endswith("withdrawn"):
            # TODO XXX (Matteo): or should we take care of withdrawn symbols?
            continue
        pharm_alternate_symbols_tokens = tokens[6].split("\"")
        pharm_alternate_symbols = set() 
        for token in pharm_alternate_symbols_tokens:
            if token != "," and len(token) > 0: 
                pharm_alternate_symbols.add(token)
        if symbol in alternate_symbols and symbol in alternate_symbols[symbol]:
            # the symbol is a 'main' symbol from hugo/hgnc, use it as it is.
            pass
        elif symbol in alternate_symbols and symbol not in alternate_symbols[symbol]:
            # the symbol is not a main symbol from hugo/hgnc, use one of its main
            # symbols (the first when the set is converted to list) as main symbol.
            # XXX (Matteo) There's no reason to choose the "first", we could
            # choose any.
            new_symbol = list(alternate_symbols[symbol])[0]
            pharm_alternate_symbols.discard(new_symbol)
            pharm_alternate_symbols.add(symbol)
            symbol = new_symbol
        elif symbol not in alternate_symbols:
            # the symbol did not appear at all in hugo/hgnc
            found_new_symbol = False
            for candidate in hgnc_alternate_symbols:
                if candidate in alternate_symbols and candidate in alternate_symbols[candidate]:
                    # we found a symbol that is an alternate symbol in pharm and
                    # a main symbol in hugo/hgnc. Elect it as main symbol for this entry
                    new_symbol = candidate
                    hgnc_alternate_symbols.discard(new_symbol)
                    hgnc_alternate_symbols.add(symbol)
                    symbol = new_symbol
                    found_new_symbol = True
                    break
            if not found_new_symbol:
                for candidate in pharm_alternate_symbols:
                    if candidate in alternate_symbols and \
                            candidate not in alternate_symbols[candidate]:
                        # we found a symbol that is an alternate symbol in
                        # pharm and an alternate symbol in hugo/hgnc. Elect the
                        # 'first' main symbol for this candidate as main symbol
                        # for this entry
                        new_symbol = list(alternate_symbols[candidate])[0]
                        pharm_alternate_symbols.discard(new_symbol)
                        pharm_alternate_symbols.add(symbol)
                        symbol = new_symbol
                        found_new_symbol = True
                        break
            if not found_new_symbol:
                # the symbol is not in hugo/hgnc at all and none of its alternate in
                # pharm appears in hugo/hgnc either. This is a completely new symbol
                alternate_symbols[symbol] = set([symbol,])
                alternate_symbols_inverted[symbol] = set([symbol,])
                long_names[symbol] = set()
        else:
            sys.stderr.write("WE SHOULDN'T BE HERE\n")
        for alternate_symbol in pharm_alternate_symbols:
            if len(alternate_symbol) == 0:
                continue
            if alternate_symbol not in alternate_symbols:
                alternate_symbols[alternate_symbol] = set([symbol,])
                alternate_symbols_inverted[symbol].add(alternate_symbol)
        name = tokens[3]
        long_names[symbol].add(name)
        pharm_alternate_names_tokens = tokens[5].split("\"")
        for token in pharm_alternate_names_tokens:
            if token != "," and len(token) > 0 and token not in long_names[symbol]:
                long_names[symbol].add(token)

for symbol in alternate_symbols:
    if len(alternate_symbols[symbol]) > 1:
        sys.stderr.write("WARNING: duplicate symbol {}: present as (alternate) symbol of {}\n".format(symbol, ", ".join(alternate_symbols[symbol])))

for symbol in alternate_symbols_inverted:
    assert symbol in long_names
    alternate_symbols_inverted[symbol].discard(symbol)
    print("{}\t{}\t{}".format(symbol,
        "|".join(alternate_symbols_inverted[symbol]),
            "|".join(long_names[symbol])))

