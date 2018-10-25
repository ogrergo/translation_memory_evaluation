#!/usr/bin/env bash

MODEL=transformer
HPARAMS=transformer_base_single_gpu
USR_DIR=../postprocessing
PROBLEM=translate_postprocess
DATA_DIR=/part/02/Tmp/experiments-meteo/TM_postprocess/data-e2f
TMP_DIR=/part/02/Tmp/experiments-meteo/TM_postprocess/output-e2f
mkdir -p $DATA_DIR $TMP_DIR


CUDA_VISIBLE_DEVICES=0 t2t-trainer \
  --generate_data \
  --t2t_usr_dir=$USR_DIR \
  --data_dir=$DATA_DIR \
  --output_dir=$TMP_DIR \
  --problem=$PROBLEM \
  --model=$MODEL \
  --hparams_set=$HPARAMS \
  --train_steps=250000 \
  --eval_steps=10000