#!/bin/bash

set -e

TRAINING_DIR="/data/corpora/training"
TUNING_DIR="/data/corpora/tuning"
MOSES_DIR="/home/moses/mosesdecoder"

FINAL_DIR="/data/model"
WORKING_DIR="/data/model/working"

mkdir -p ${WORKING_DIR}

cd ${WORKING_DIR}

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l en  <${TRAINING_DIR}/commoncrawl.de-en.en  >commoncrawl.de-en.tok.en

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l de  <${TRAINING_DIR}/commoncrawl.de-en.de  >commoncrawl.de-en.tok.de

${MOSES_DIR}/scripts/recaser/train-truecaser.perl --model  truecase-model.en --corpus commoncrawl.de-en.tok.en

${MOSES_DIR}/scripts/recaser/train-truecaser.perl --model  truecase-model.de --corpus commoncrawl.de-en.tok.de

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.en   <commoncrawl.de-en.tok.en  >commoncrawl.de-en.true.en

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.de   <commoncrawl.de-en.tok.de  >commoncrawl.de-en.true.de

${MOSES_DIR}/scripts/training/clean-corpus-n.perl   commoncrawl.de-en.true de en commoncrawl.de-en.clean 1 80

echo "Training preparation complete!"

${MOSES_DIR}/bin/lmplz -o 3 <commoncrawl.de-en.true.en   >commoncrawl.de-en.arpa.en

${MOSES_DIR}/bin/build_binary commoncrawl.de-en.arpa.en commoncrawl.de-en.blm.en

${MOSES_DIR}/scripts/training/train-model.perl --root-dir train  \
   -corpus ${WORKING_DIR}/commoncrawl.de-en.clean -f de -e en -alignment grow-diag-final-and \
   -reordering msd-bidirectional-fe -lm 0:3:${WORKING_DIR}/commoncrawl.de-en.blm.en:8 \
   -external-bin-dir ${MOSES_DIR}/tools >& training.out

tail training.out

echo "Training complete!"

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l en <${TUNING_DIR}/newstest2012.en >newstest2012.tok.en

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l de <${TUNING_DIR}/newstest2012.de >newstest2012.tok.de

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.en   <newstest2012.tok.en >newstest2012.true.en

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.de   <newstest2012.tok.de >newstest2012.true.de

echo "Tuning preparation complete!"

cd ${FINAL_DIR}

${MOSES_DIR}/scripts/training/mert-moses.pl  ${WORKING_DIR}/newstest2012.true.de  \
   ${WORKING_DIR}/newstest2012.true.en ${MOSES_DIR}/bin/moses  ${WORKING_DIR}/train/model/moses.ini  \
   --mertdir ${MOSES_DIR}/bin &>mert.out 

tail mert.out

echo "Tuning complete!"

# TODO once it works
# rm -fr ${WORKING_DIR}
