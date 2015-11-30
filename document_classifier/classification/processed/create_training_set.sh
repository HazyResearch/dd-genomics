#! /bin/zsh -x

../extract_sentences_from_db.sh > genomics_production_2_sentences_gm_pm.tsv
mv genomics_production_2_sentences.tsv split
cd split
split -l 10000 -a 4 genomics_production_2_sentences.tsv
mv genomics_production_2_sentences.tsv ..
cd ..
ls split/* | xargs -P 80 -I % ./genomics_dump_to_processed.py % %.processed
cat split/*.processed > genomics_production_2_sentences.tsv
shuf genomics_production_2_sentences.tsv > genomics_production_2_sentences_random.tsv
cat processed/genomics_production_2_sentences_random.tsv | awk -F '\t' '{if ($3 == "1") print $0}' > training_set.tsv

qwer_count=$1
zxcv_count=$2
all_count=`cat genomics_production_2_sentences_random.tsv | wc -l`
((asdf_count=$all_count - $qwer_count - $zxcv_count))
((asdf_qwer_count=$asdf_count + $qwer_count))

head -n $asdf_count genomics_production_2_sentences_random.tsv > subset1
tail -n+$asdf_count genomics_production_2_sentences_random.tsv | head -n $qwer_count > ../qwer
tail -n+$asdf_qwer_count genomics_production_2_sentences_random.tsv | head -n $zxcv_count > ../zxcv
cat subset1 | awk -F '\t' '{if ($3 == "1") print $0}' > ../asdf
cat subset1 | awk -F '\t' '{if ($3 == "0") print $0}' | head -n 40000 >> ../asdf

