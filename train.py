#!/usr/bin/env python3
import argparse
import os.path
import subprocess
from datetime import datetime


def set_working_directory(options):
    # Do nothing if the user set the directory
    if not options.working_dir:
        timestamp = datetime.now().isoformat().split('.')[0].replace('-', '').replace(':', '')
        # e.g., '20190110T125556'
        subdirectory = 'working_%s' % timestamp
        options.working_dir = os.path.join(options.output_dir, subdirectory)
    options.working_file_base = os.path.join(options.working_dir,
                                             os.path.basename(options.input_base))
    return


def run_command(command, options, infile=None, outfile=None, errfile=None):
    print('$  %s' % ' '.join(command))
    if infile:
        print('  <', infile)
    if outfile:
        print('  >', outfile)
    if not options.dry_run:
        if errfile is None:
            errfile = subprocess.PIPE
        p = subprocess.run(command, stdin=infile, stdout=outfile, stderr=errfile)
        print(p.stderr)
    print()
    return


oparser = argparse.ArgumentParser(description='Train a Moses model from a standard training set')

oparser.add_argument('-n', dest='dry_run',
                     default=False, action='store_true',
                     help='dry run')

oparser.add_argument('-s', dest='source_language',
                     default='ru',
                     help='source language')

oparser.add_argument('-t', dest='target_language',
                     default='en', type=str,
                     help='target language (default en)')

oparser.add_argument('-o', dest='output_dir',
                     default='/data/models/output',
                     help='model output directory')

oparser.add_argument('-u', dest='tuning_base',
                     default='/data/training/tuning/newstest2013',
                     help='tuning files without "." and 2-letter language code extension')

oparser.add_argument('-w', dest='working_dir',
                     default=None,
                     help='working directory for training data')

oparser.add_argument('-m', dest='moses_dir',
                     default='/home/moses/mosesdecoder/',
                     help='moses directory (usually called "mosesdecoder"; '
                          'contains scripts and bin subdirectories)')

oparser.add_argument('-i', dest='input_base',
                     default='/data/training/training-commoncrawl/commoncrawl.ru-en',
                     help='input filenames without "." and 2-letter language code extension')

options = oparser.parse_args()


set_working_directory(options)

if not options.dry_run:
    os.makedirs(options.working_dir, exist_ok=True)
    os.makedirs(options.output_dir, exist_ok=True)

print('Output directory', options.output_dir)
print('Working directory', options.working_dir)
print()

tokenizer = os.path.join(options.moses_dir, 'scripts', 'tokenizer', 'tokenizer.perl')
truecase_trainer = os.path.join(options.moses_dir, 'scripts', 'recaser', 'train-truecaser.perl')
truecaser = os.path.join(options.moses_dir, 'scripts', 'recaser', 'truecase.perl')
cleaner = os.path.join(options.moses_dir, 'scripts', 'training', 'clean-corpus-n.perl')
lmplz = os.path.join(options.moses_dir, 'bin', 'lmplz')
builder = os.path.join(options.moses_dir, 'bin', 'build_binary')
trainer = os.path.join(options.moses_dir, 'scripts', 'training', 'train-model.perl')

tools_dir = os.path.join(options.moses_dir, 'tools')

tokenized_source = options.working_file_base + '.tok.' + options.source_language
tokenized_target = options.working_file_base + '.tok.' + options.target_language
true_source_model = os.path.join(options.output_dir, 'truecase-model.%s' % options.source_language)
true_target_model = os.path.join(options.output_dir, 'truecase-model.%s' % options.target_language)
trued_base = options.working_file_base + '.true'
trued_source = trued_base + '.' + options.source_language
trued_target = trued_base + '.' + options.target_language
cleaned_file = options.working_file_base + '.clean'
arpa_file = options.working_file_base + '.arpa.' + options.target_language
blm_file = options.working_file_base + '.blm.' + options.target_language
train_dir = os.path.join(options.output_dir, 'train')
training_out = os.path.join(options.working_dir, 'training.out')

# https://stackoverflow.com/questions/4965159/python-how-to-redirect-output-with-subprocess
# subprocess.call(command, stdout=FILE, ...)

# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en
#    <news-commentary-v9.ru-en.en >news-commentary-v9.ru-en.tok.en
# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l ru
#    <news-commentary-v9.ru-en.ru >news-commentary-v9.ru-en.tok.ru

with open('%s.%s' % (options.input_base, options.source_language)) as infile, open(tokenized_source, 'w') as outfile:
    command = [tokenizer, '-l', options.source_language]
    run_command(command, options, infile=infile, outfile=outfile)

with open('%s.%s' % (options.input_base, options.target_language)) as infile, open(tokenized_target, 'w') as outfile:
    command = [tokenizer, '-l', options.target_language]
    run_command(command, options, infile=infile, outfile=outfile)

# /home/moses/mosesdecoder/scripts/recaser/train-truecaser.perl --model
#   /data/models/truecase-model.en --corpus news-commentary-v9.ru-en.tok.en
# /home/moses/mosesdecoder/scripts/recaser/train-truecaser.perl --model
#   /data/models/truecase-model.ru --corpus news-commentary-v9.ru-en.tok.ru

command = [truecase_trainer, '--model', true_source_model, '--corpus', tokenized_source]
run_command(command, options)

command = [truecase_trainer, '--model', true_target_model, '--corpus', tokenized_target]
run_command(command, options)

# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.en
#   <news-commentary-v9.ru-en.tok.en  > news-commentary-v9.ru-en.true.en
# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.ru
#   <news-commentary-v9.ru-en.tok.ru  > news-commentary-v9.ru-en.true.ru

with open(tokenized_source) as infile, open(trued_source, 'w') as outfile:
    command = [truecaser, '--model', true_source_model, '<', tokenized_source, '>', trued_source]
    run_command(command, options, infile=infile, outfile=outfile)

with open(tokenized_target) as infile, open(trued_target, 'w') as outfile:
    command = [truecaser, '--model', true_target_model]
    run_command(command, options, infile=infile, outfile=outfile)

# /home/moses/mosesdecoder/scripts/training/clean-corpus-n.perl
#   news-commentary-v9.ru-en.true ru en news-commentary-v9.ru-en.clean 1 80
# /home/moses/mosesdecoder/bin/lmplz -o 3 <news-commentary-v9.ru-en.true.en
#   >news-commentary-v9.ru-en.arpa.en
# /home/moses/mosesdecoder/bin/build_binary news-commentary-v9.ru-en.arpa.en news-commentary-v9.ru-en.blm.en

command = [cleaner, trued_base, options.target_language, options.source_language,
           cleaned_file, '1', '80']
run_command(command, options)

with open(trued_target) as infile, open(arpa_file, 'w') as outfile:
    command = [lmplz, '-o', '3']
    run_command(command, options, infile=infile, outfile=outfile)

command = [builder, arpa_file, blm_file]
run_command(command, options)

# nohup /home/moses/mosesdecoder/scripts/training/train-model.perl --root-dir train
# -corpus /data/adam/training-nc-v9/news-commentary-v9.ru-en.clean -f ru -e en -alignment grow-diag-final-and
# -reordering msd-bidirectional-fe -lm 0:3:/data/adam/training-nc-v9/news-commentary-v9.ru-en.blm.en:8
# -external-bin-dir /home/moses/mosesdecoder/tools >& training.out &

if not options.dry_run:
    os.makedirs(train_dir, exist_ok=True)

with open(training_out, 'w') as errfile:
    command = [trainer, '--root-dir', train_dir, '-corpus', cleaned_file, '-f', options.source_language,
               '-e', options.target_language, '-alignment', 'grow-diag-final-and',
               '-reordering', 'msd-bidirectional-fe', '-m', '0:3:%s:8' % blm_file,
               '-external-bin-dir', tools_dir]
    run_command(command, options, outfile=errfile, errfile=errfile)

working_tuning_base = os.path.join(options.working_dir, os.path.basename(options.tuning_base))
tokenized_tuning_source = working_tuning_base + '.tok.' + options.source_language
tokenized_tuning_target = working_tuning_base + '.tok.' + options.target_language
trued_tuning_source = working_tuning_base + '.true.' + options.source_language
trued_tuning_target = working_tuning_base + '.true.' + options.target_language

# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l en <newstest2013.en >newstest2013.tok.en
# /home/moses/mosesdecoder/scripts/tokenizer/tokenizer.perl -l ru <newstest2013.ru >newstest2013.tok.ru

with open('%s.%s' % (options.tuning_base, options.source_language)) as infile, open (tokenized_tuning_source, 'w') as outfile:
    command = [tokenizer, '-l', options.source_language]
    run_command(command, options, infile=infile, outfile=outfile)

with open('%s.%s' % (options.tuning_base, options.target_language)) as infile, open(tokenized_tuning_target, 'w') as outfile:
    command = [tokenizer, '-l', options.target_language]
    run_command(command, options, infile=infile, outfile=outfile)

# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.en
#    <newstest2013.tok.en >newstest2013.true.en
# /home/moses/mosesdecoder/scripts/recaser/truecase.perl --model /data/models/truecase-model.ru
#    <newstest2013.tok.ru >newstest2013.true.ru

with open(tokenized_tuning_source) as infile, open(trued_tuning_source, 'w') as outfile:
    command = [truecaser, '--model', true_source_model]
    run_command(command, options, infile=infile, outfile=outfile)

with open(tokenized_tuning_target) as infile, open(trued_tuning_target, 'w') as outfile:
    command = [truecaser, '--model', true_target_model]
    run_command(command, options, infile=infile, outfile=outfile)

# nohup /home/moses/mosesdecoder/scripts/training/mert-moses.pl /data/adam/tuning/newstest2013.true.ru
#  /data/adam/tuning/newstest2013.true.en /home/moses/mosesdecoder/bin/moses train/model/moses.ini
#  --mertdir /home/moses/mosesdecoder/bin &>mert.out &

merter = os.path.join(options.moses_dir, 'scripts', 'training', 'mert-moses.pl')
moses_bin = os.path.join(options.moses_dir, 'bin', 'moses')
old_moses_ini = os.path.join(train_dir, 'model', 'moses.ini')
mert_out = os.path.join(options.working_dir, 'mert.out')

with open(mert_out, 'w') as errfile:
    command = [merter, trued_tuning_source, trued_tuning_target, moses_bin, old_moses_ini,
               '--mertdir', os.path.join(options.moses_dir, 'bin')]
    run_command(command, options, outfile=errfile, errfile=errfile)
