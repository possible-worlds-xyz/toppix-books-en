wget https://dumps.wikimedia.org/enwiki/latest/
cat index.html |egrep "multistream[0-9]"|sed "s/<a href=\"//"|sed "s/\".*//"|egrep -v "rss|txt\.bz2"|sed "s/^/https:\/\/dumps\.wikimedia\.org\/enwiki\/latest\//" > latest_wiki_paths.txt
rm -f index.html

