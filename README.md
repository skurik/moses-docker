# moses-docker
An Ubuntu 18.10-based dockerfile for running [Moses](http://www.statmt.org/moses)

To create the image, run

    $ git clone https://github.com/skurik/moses-docker.git
    $ cd moses-docker
    $ docker build -t <user>/moses .
    
To run the container, execute

    $ docker run -t -i <user>/moses /bin/bash
    
Now you can verify that Moses is working:

    $ root@5618c50d37eb:/home/moses# cd sample-models
    $ root@5618c50d37eb:/home/moses# ../mosesdecoder/bin/moses -f phrase-model/moses.ini < phrase-model/in
    ...
    Translating: das ist ein kleines haus
    BEST TRANSLATION: this is a small house [11111]  [total=-28.923] core=(-27.091,0.000,-5.000,0.000,-1.833)

# Requirements

As compiling [boost](http://www.boost.org) is part of building the image, I recommend to have at least 5 GB of RAM.
