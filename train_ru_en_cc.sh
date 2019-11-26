#!/bin/bash

set -e

TRAINING_DIR="/data/corpora/training"
TUNING_DIR="/data/corpora/tuning"
MOSES_DIR="/home/moses/mosesdecoder"

FINAL_DIR="/data/model"
WORKING_DIR="/data/model/working"

mkdir -p ${WORKING_DIR}

cd ${WORKING_DIR}

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l en  <${TRAINING_DIR}/commoncrawl.ru-en.en  >commoncrawl.ru-en.tok.en

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l ru  <${TRAINING_DIR}/commoncrawl.ru-en.ru  >commoncrawl.ru-en.tok.ru

${MOSES_DIR}/scripts/recaser/train-truecaser.perl --model  truecase-model.en --corpus commoncrawl.ru-en.tok.en

${MOSES_DIR}/scripts/recaser/train-truecaser.perl --model  truecase-model.ru --corpus commoncrawl.ru-en.tok.ru

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.en   <commoncrawl.ru-en.tok.en  >commoncrawl.ru-en.true.en

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.ru   <commoncrawl.ru-en.tok.ru  >commoncrawl.ru-en.true.ru

${MOSES_DIR}/scripts/training/clean-corpus-n.perl   commoncrawl.ru-en.true ru en commoncrawl.ru-en.clean 1 80

echo "Training preparation complete!"

${MOSES_DIR}/bin/lmplz -o 3 <commoncrawl.ru-en.true.en   >commoncrawl.ru-en.arpa.en

${MOSES_DIR}/bin/build_binary commoncrawl.ru-en.arpa.en commoncrawl.ru-en.blm.en

${MOSES_DIR}/scripts/training/train-model.perl --root-dir train  \
   -corpus ${WORKING_DIR}/commoncrawl.ru-en.clean -f ru -e en -alignment grow-diag-final-and \
   -reordering msd-bidirectional-fe -lm 0:3:${WORKING_DIR}/commoncrawl.ru-en.blm.en:8 \
   -external-bin-dir ${MOSES_DIR}/tools >& training.out

tail training.out

echo "Training complete!"

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l en <${TUNING_DIR}/newstest2012.en >newstest2012.tok.en

${MOSES_DIR}/scripts/tokenizer/tokenizer.perl -l ru <${TUNING_DIR}/newstest2012.ru >newstest2012.tok.ru

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.en   <newstest2012.tok.en >newstest2012.true.en

${MOSES_DIR}/scripts/recaser/truecase.perl --model truecase-model.ru   <newstest2012.tok.ru >newstest2012.true.ru

echo "Tuning preparation complete!"

cd ${FINAL_DIR}

${MOSES_DIR}/scripts/training/mert-moses.pl  ${WORKING_DIR}/newstest2012.true.ru  \
   ${WORKING_DIR}/newstest2012.true.en ${MOSES_DIR}/bin/moses  ${WORKING_DIR}/train/model/moses.ini  \
   --mertdir ${MOSES_DIR}/bin &>mert.out 

tail mert.out

echo "Tuning complete!"

# TODO once it works
# rm -fr ${WORKING_DIR}
