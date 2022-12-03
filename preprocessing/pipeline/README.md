# Pipeline for preprocessing

This directory contains everything needed to set up a preprocessing pipeline for wikipedia movies. 

NB1: the wikiextractor folder contains a modified version of the original code (see below). To use it, pip install wikiextractor normally, then go into lib/python3.7/site-packages/wikiextractor and replace the .py files with the ones contained in this directory.

NB2: the neuralcoref code is also here, but it should be used in a separate virtualenv, using huggingface's instructions for an install from source. Basically:

    git clone https://github.com/huggingface/neuralcoref.git
    cd neuralcoref
    pip install -r requirements.txt
    pip install -e .

This is because neuralcoref requires a specific (older) version of spacy.



## Downloader

Download stuff from Wikipedia to <some large folder>/<date>.

Before any processing, get the latest wiki file list by running:

    ./get_latest_wiki_filenames.sh

Then, download and filter the movies:

    python3 get_books_xml.py

WARNING: for now, the base_dir <some large folder>/<date> has to be set manually in all subsequent scripts.


## Wikiextractor

Now, convert to linear format, using Wikiextractor.

| IMPORTANT:
| 
| Change lib/python3.7/site-packages/wikiextractor/extract.py to set mark_headers = True in two places.
| Also change lib/python3.7/site-packages/wikiextractor/WikiExtractor.py so that output can be a file and not a ridiculous collection of folders.
| 
| !! Keep current version in lib/, otherwise, the work has to be done again!




## Processing

First, process the XML to get titles, excerpts, infoboxes, categories, locations, times, dependencies, etc.

    python3 process_films.py

WARNING: At the moment, the function mk_movie_titles only keep movies with a description length of > 500 characters, resulting in around 36,000 movies kept from a whole list of around 140,000. This can be changed.


Second, run neuralcoref to get character information. This has to be done from a different virtualenv because neuralcoref is annoying. See relevant README.


Third, run TMDB processing. This will take a while because we're sleeping 2s between calls to be nice to the TMDB API. Go to bed for a couple of days.

    python3 process_tmdb.py

