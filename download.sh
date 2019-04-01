#!/bin/bash

set -e

#  http://www.statmt.org/moses/?n=Moses.LinksToCorpora
#  "This page is your 'shopping list' for parallel texts."

mkdir -p /data/corpora/training
cd /data/corpora
wget http://www.statmt.org/wmt13/training-parallel-commoncrawl.tgz
wget http://www.statmt.org/wmt13/dev.tgz

cd training
tar zxf ../training-parallel-commoncrawl.tgz
cd ..
tar zxf dev.tgz
# unpacks into dev/*
mv dev tuning

# now we only need the unpacked data
rm training-parallel-commoncrawl.tgz dev.tgz
