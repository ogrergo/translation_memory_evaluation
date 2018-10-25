#!/usr/bin/env bash

MODEL=transformer
HPARAMS=transformer_base_single_gpu
USR_DIR=/u/vanbeurl/code/scrap_warns/TM2/postprocessing
PROBLEM=translate_postprocess
DATA_DIR=/data/rali6/Tmp/vanbeurl/meteo-data/TM_postprocess/data
TMP_DIR=/data/rali6/Tmp/vanbeurl/meteo-data/TM_postprocess/output

BEAM_SIZE=4
ALPHA=0.6

DECODE_FILE='/data/rali6/Tmp/vanbeurl/meteo-data/TM_postprocess/sftp-test-clean.WattTokenize.RemovePunct.RemoveSpaces.en'
OUT_DECODE_FILE='/data/rali6/Tmp/vanbeurl/meteo-data/TM_postprocess/decode/sftp-test-clean.WattTokenize.RemovePunct.RemoveSpaces.en.tgt'

export CUDA_VISIBLE_DEVICES="1"

t2t-decoder \
  --t2t_usr_dir=$USR_DIR \
  --data_dir=$DATA_DIR \
  --problem=$PROBLEM \
  --model=$MODEL \
  --hparams_set=$HPARAMS \
  --output_dir=$TMP_DIR \
  --decode_hparams="beam_size=$BEAM_SIZE,alpha=$ALPHA" \
  --decode_from_file=$DECODE_FILE \
  --decode_to_file=$OUT_DECODE_FILE \
  --worker_gpu=1
