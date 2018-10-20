#!/usr/bin/env bash

DATA_FOLDER=/data/rali6/Tmp/vanbeurl/meteo-data/


MOSESDECODER=/u/vanbeurl/code/scrap_warns/datasets/tools/mosesdecoder

CLEAN_CORPUS=$MOSESDECODER/scripts/tokenizer/pre_tokenize_cleaning.py
UNRAVEL_CLEAN=split_corpus.py


for e in sftp portage watt sftp-test
do
    fr="$DATA_FOLDER/$e.fr"
    en="$DATA_FOLDER/$e.en"

    fr_out="$DATA_FOLDER/$e-clean.fr"
    en_out="$DATA_FOLDER/$e-clean.en"

    echo "Processing $e ..."

    python $CLEAN_CORPUS $fr $en > /tmp/corpus_cleaned
    python $UNRAVEL_CLEAN /tmp/corpus_cleaned $fr_out $en_out
done