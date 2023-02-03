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

You will need virtualenv installed on your machine.

```
git clone https://github.com/possible-worlds-xyz/toppix-books-en.git
virtualenv toppix-books-en/
cd toppix-books-en/
source bin/activate
pip install -r requirements.txt
cp -r preprocessing/pipeline/wikiextractor/ lib/python3.8/site-packages/
```

For the last command, replace *python3.8* with whichever python version you may be running in your virtualenv.

## Preprocessing

The first thing you'll want to do is get the latest Wikipedia dump, preprocessed to include books only. Head over to your *preprocessing/pipeline* directory and run:

```
cd preprocessing/pipeline/
./get_latest_wiki_filenames.sh
python3 get_books_xml.py 
```

You will now have a file listing the paths of the latest wiki dump, at *latest_wiki_paths.txt* in your pipeline folder. In addition, a newly created directory will be available under *wikipedia/<today' date>*, containing an xml folder. In the xml folder, you will find zipped files of your Wikipedia dump, preprocessed to only retain book-related pages.

The last thing to do is to launch the feature extraction on the xml folder. Let us say that the date of your wikipedia folder is 2023-02-01, then you would launch the extraction with:

```
python3 process_books.py wikipedia/2023-02-01/
```

The result of this step will be a set of additional folders in *wikipedia/2023-02-01/*: 

```
|categorisation
|linear
|parsed
```

The linear folder contains the text of the Wikipedia documents with markup removed. The categorisation folder contains various types of information, from location and time categories to broad topical features. Finally, the parsed directory contains a dependency-parsed version of the corpus, which can be used for more fine-grained analysis.


## Setting up the API

Now, head over to your *django-backend* folder and set up your API:

```
python3 manage.py migrate
python3 manage.py createsuperuser
python3 populate.py ../../preprocessing/pipeline/wikipedia/2023-02-01/
```

(Amend the path in the populate command according to the directory path you obtained in the preprocessing step.)

That's it! Now launch your server:

```
python3 manage.py runserver
```

You should now be able to navigate your API from your browser, e.g. by visiting

[http://localhost:8000/toppixapi/books/topic/horses/1/](http://localhost:8000/toppixapi/books/topic/horses/1/)
