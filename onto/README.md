### Onto: supporting data files \& utilitity scripts

* `data/`: processed supporting data (e.g. created via scripts called in `make_all.sh`)
* `raw/`: raw unprocessed downloads e.g. pulled from web during `make_all.sh`
* `dicts/`: static dictionaries not dynamically loaded
* `manual/`: manually-curated dictionaries

Running `make_all.sh` should perform all operations to populate `data/` (and `raw/`).
