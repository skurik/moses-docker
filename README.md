# moses-docker
An Ubuntu 18.10-based dockerfile for running [Moses](http://www.statmt.org/moses)

To create the image:

    $ git clone https://github.com/adam-funk/moses-docker.git
    $ cd moses-docker
    $ docker build -t moses .

To download the training and tuning data (you only need to do this once; keep the `moses-data` volume for subsequent training runs):

    $ docker volume create moses-data
    $ docker run --mount type=volume,src=moses-data,dst=/data/corpora -t -i moses
    # ./download.sh

To train a model (final output is based on `/data/models/mert-work/moses-ini`, which points to other data files):
   
    $ docker volume create moses-ru-en
    $ docker run --mount type=volume,src=moses-data,dst=/data/corpora --mount type=volume,src=moses-ru-en,dst=/data/model --rm -t -i moses
    # ./train_ru_en.sh

    $ docker volume create moses-de-en
    $ docker run --mount type=volume,src=moses-data,dst=/data/corpora --mount type=volume,src=moses-de-en,dst=/data/model --rm -t -i moses
    # ./train_de_en.sh

To run the service (you can change the published port):

    $ docker run --mount type=volume,src=moses-ru-en,dst=/data/model -p 8080:8080 -t -i moses
    # ./server.sh

# Notes

- It takes quite a bit of memory to build cmph, giza, and moses: better to build the image on the server than on a laptop.

- No longer compiling boost (the Ubuntu 18.10 package is recent enough).

- You can create the `moses-data` volume and download the data once, keeping the volume for re-use with different language combinations.

- Training requires the `moses-data` volume and another volume to build the intermediate and final models in.

- Running the service requires only the volume with the trained models.

- The service runs on port 8080 inside the container, but you can publish it to any port.

# Moses documentation

- <http://www.statmt.org/moses/?n=Moses.Baseline>

- <http://www.statmt.org/moses/?n=Advanced.Moses>

# TODO

- Python client library

- Fix the entrypoint system and make readable log files
