# moses-docker
An Ubuntu 18.10-based dockerfile for running [Moses](http://www.statmt.org/moses)

To create the image:

    $ git clone https://github.com/adam-funk/moses-docker.git
    $ cd moses-docker
    $ docker build -t moses .

To download the training and tuning data (you only need to do this once; keep the moses-data volume for subsequent training runs):

    $ docker volume create moses-data
    $ docker run --mount type=volume,src=moses-data,dst=/data/corpora -t -i moses
    # ./download.sh

To train a model (final file is `/data/models/mert-work/moses-ini`):
   
    $ docker volume create moses-ru-en
    $ docker run --mount type=volume,src=moses-data,dst=/data/corpora --mount type=volume,src=moses-ru-en,dst=/data/model -rm -t -i moses
    # ./train_ru_en.sh

To run the service:

    $ docker run --mount type=volume,src=moses-ru-en,dst=/data/model -t -i moses
    # ...

# Notes

- It takes quite a bit of memory to build cmph, giza, and moses: better to build the image on the server than on a laptop.

- No longer compiling boost (the Ubuntu 18.10 package is recent enough).


# TODO

- WIP: replace the python script with separate working bash scripts for the languages, using common crawl corpora
- WIP: use two volumes: one for downloaded data, the other for the models
- include server running script in docker image
- provide sh scripts for building and running docker image
