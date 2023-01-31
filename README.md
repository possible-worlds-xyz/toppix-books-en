<table style="border:0px;">
<tr><td><img src="img/redmoonlogo.png" width="50px"/></td><td><h1>Toppix for English books</h1></td></tr>
</table>

Toppix is a privacy-friendly recommendation engine for books and movies. It provides users with fine-grained search features, letting them browse through story locations, topics, settings, character types and more. All this without any personal data collection. You can try the Toppix prototype at [https://toppix.pw/](https://toppix.pw/).

## The repository

This repo contains two main directories, *preprocessing* and *django-backend*. In *preprocessing*, you will find all scripts needed to extract book information from the English Wikipedia. In *django-backend*, there is code to populate a database with the extracted information and set up an API. To find out what the official Toppix API currently looks like, you can try the following queries in your browser:


* Title search: [https://possibleworlds.eu.pythonanywhere.com/toppixapi/books/titles/A%20Column%20of%20Fire/](https://possibleworlds.eu.pythonanywhere.com/toppixapi/books/titles/A%20Column%20of%20Fire/)
* Topic search: [https://possibleworlds.eu.pythonanywhere.com/toppixapi/books/topic/dogs/1/](https://possibleworlds.eu.pythonanywhere.com/toppixapi/books/topic/dogs/1/)
* Setting search: [https://possibleworlds.eu.pythonanywhere.com/toppixapi/books/country/Japan/1/](https://possibleworlds.eu.pythonanywhere.com/toppixapi/books/country/Japan/1/)


## Installation

'''
git clone https://github.com/possible-worlds-xyz/toppix-books-en.git
./virtualenv toppix-books-en/
cd toppix-books-en/
source bin/activate
pip install -r requirements.txt
cp -r preprocessing/pipeline/wikiextractor/ lib/python3.8/site-packages/
'''

## Preprocessing

The first thing you'll want to do is get the latest Wikipedia dump, preprocessed to include books only. Head over to your *preprocessing/pipeline* directory and run:

'''
cd preprocessing/pipeline/
./get_latest_wiki_filenames.sh
python3 get_books_xml.py 
'''

You will now have a file listing the paths of the latest wiki dump, at *latest_wiki_paths.txt*.

## Setting up the API
