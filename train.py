#!/usr/bin/env python3
import argparse

oparser = argparse.ArgumentParser(description='Train a Moses model from a standard training set')

oparser.add_argument('-d', dest='debug',
                     default=False, action='store_true',
                     help='debugging')

oparser.add_argument('-m', dest='model_dir',
                     default=None,
                     help='model output directory (required)')

oparser.add_argument('-d', dest='moses_dir',
                     default=None,
                     help='moses directory (required; usually called "mosesdecoder"; '
                          'contains scripts and bin subdirectories)')

# There should be one input file?

oparser.add_argument(dest='input_files', metavar='FILE',
                     nargs='*', type=str,
                     help='input files')

options = oparser.parse_args()



#
# cd /data/adam/training-nc-v9/
#
# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en <news-commentary-v9.ru-en.en >news-commentary-v9.ru-en.tok.en
#
# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l ru <news-commentary-v9.ru-en.ru >news-commentary-v9.ru-en.tok.ru
#
# /home/moses/mosesdecoder/scripts/recaser/train-truecaser.perl --model /data/models/truecase-model.en --corpus news-commentary-v9.ru-en.tok.en
#
# /home/moses/mosesdecoder/scripts/recaser/train-truecaser.perl --model /data/models/truecase-model.ru --corpus news-commentary-v9.ru-en.tok.ru
#
# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.en  <news-commentary-v9.ru-en.tok.en  > news-commentary-v9.ru-en.true.en
#
# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.ru  <news-commentary-v9.ru-en.tok.ru  > news-commentary-v9.ru-en.true.ru
#
# /home/moses/mosesdecoder/scripts/training/clean-corpus-n.perl news-commentary-v9.ru-en.true ru en news-commentary-v9.ru-en.clean 1 80
#
# /home/moses/mosesdecoder/bin/lmplz -o 3 <news-commentary-v9.ru-en.true.en >news-commentary-v9.ru-en.arpa.en
#
# /home/moses/mosesdecoder/bin/build_binary news-commentary-v9.ru-en.arpa.en news-commentary-v9.ru-en.blm.en
#
# mkdir /data/models/working
#
# cd /data/models/working
#
# nohup /home/moses/mosesdecoder/scripts/training/train-model.perl --root-dir train -corpus /data/adam/training-nc-v9/news-commentary-v9.ru-en.clean -f ru -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:3:/data/adam/training-nc-v9/news-commentary-v9.ru-en.blm.en:8 -external-bin-dir /home/moses/mosesdecoder/tools >& training.out &
#
#
# cd /data/adam/tuning
#
# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en <newstest2013.en >newstest2013.tok.en
#
# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l ru <newstest2013.ru >newstest2013.tok.ru
#
# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.en <newstest2013.tok.en >newstest2013.true.en
#
# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.ru <newstest2013.tok.ru >newstest2013.true.ru
#
# cd /data/models/working
#
# nohup /home/moses/mosesdecoder/scripts/training/mert-moses.pl /data/adam/tuning/newstest2013.true.ru /data/adam/tuning/newstest2013.true.en /home/moses/mosesdecoder/bin/moses train/model/moses.ini --mertdir /home/moses/mosesdecoder/bin &>mert.out &
#
# cd /data/models
#
# /home/moses/mosesdecoder/bin/moses -f mert-work/moses.ini --server --server-log /data/adam/moses-server.log
