#!/usr/bin/env bash

USR_DIR=../postprocessing
PROBLEM=translate_postprocess
DATA_DIR=/part/02/Tmp/experiments-meteo/TM_postprocess/data
TMP_DIR=/part/02/Tmp/experiments-meteo/TM_postprocess/output
mkdir -p $DATA_DIR $TMP_DIR


t2t-trainer \
  --t2t_usr_dir=$USR_DIR \
  --data_dir=$DATA_DIR \
  --output_dir=$TMP_DIR \
  --problem=translate_postprocess \
  --model=transformer \
  --hparams_set=transformer_base_single_gpu \
  --train_steps=100000 \
  --eval_steps=10000