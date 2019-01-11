#!/bin/sh

./train.py -s ru -t en -o /data/models/ -w /data/models/working -u /data/training/tuning/newstest2013 -m mosesdecoder/ -i /data/training/training-commoncrawl/commoncrawl.ru-en
