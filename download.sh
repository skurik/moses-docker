#!/bin/bash

#  http://www.statmt.org/moses/?n=Moses.LinksToCorpora
#  "This page is your 'shopping list' for parallel texts."

mkdir -p corpora/training
cd corpora
wget http://www.statmt.org/wmt13/training-parallel-commoncrawl.tgz
wget http://www.statmt.org/wmt13/dev.tgz

cd training
tar zxf ../training-parallel-commoncrawl.tgz
cd ..
tar zxv dev.tgz
# unpacks into dev/*
mv dev tuning

# ~/corpora/training/*
# ~/corpora/tuning/*

