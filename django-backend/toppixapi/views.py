
# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only

from .models import Book, Topic, Continent, Country, Time, Character
from .serializers import BookSerializer, FullBookSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

# Define class to convert all records of the customers table into JSON
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class GetBooksByTitle(viewsets.ViewSet):
    def list(self, request, title):
        books = Book.objects.filter(title=title)
        serializer = FullBookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetBooksByFemaleLead(viewsets.ViewSet):
    def list(self, request, female_lead):
        books = Book.objects.filter(female_lead=female_lead)
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPaginatedBooksByFemaleLead(viewsets.ViewSet):
    def list(self, request, female_lead, page):
        start_book = (page - 1) * 100
        books = Book.objects.filter(female_lead=female_lead)[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPaginatedBooksByContinent(viewsets.ViewSet):
    def list(self, request, continent, page):
        continent = Continent.objects.get(continent=continent)
        start_book = (page - 1) * 100
        books = continent.books.all().order_by('-release_date')[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetBooksByContinent(viewsets.ViewSet):
    def list(self, request, continent):
        continent = Continent.objects.get(continent=continent)
        books = continent.books
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPaginatedBooksByCountry(viewsets.ViewSet):
    def list(self, request, country, page):
        country = Country.objects.get(country=country)
        start_book = (page - 1) * 100
        books = country.books.all().order_by('-release_date')[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetBooksByCountry(viewsets.ViewSet):
    def list(self, request, country):
        country = Country.objects.get(country=country)
        books = country.books
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPaginatedBooksByTime(viewsets.ViewSet):
    def list(self, request, time, page):
        time = Time.objects.get(rangeStart=time)
        start_book = (page - 1) * 100
        books = time.books.all().order_by('-release_date')[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPaginatedBooksByTopic(viewsets.ViewSet):
    def list(self, request, topic, page):
        topic = Topic.objects.get(topic=topic)
        start_book = (page - 1) * 100
        books = topic.books.all().order_by('-release_date')[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPaginatedBooksByAgeRange(viewsets.ViewSet):
    def list(self, request, age_range, page):
        start_book = (page - 1) * 100
        books = Book.objects.filter(characters__in=Character.objects.filter(age_range=age_range)).order_by('-release_date')[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetBooksByMultiple(viewsets.ViewSet):
    def list(self, request, topic, country, time):
        print("PARAMS:",topic, country,time)
        list_of_matches = []
        try:
            topic = Topic.objects.get(topic=topic)
            list_of_matches.append(topic.books.all())
        except:
            print("Topic",topic,"not found.")
        try:
            country = Country.objects.get(country=country)
            list_of_matches.append(country.books.all())
        except:
            print("Country",country,"not found.")
        try:
            time = Time.objects.get(rangeStart=time)
            list_of_matches.append(time.books.all())
        except:
            print("Time",time,"not found.")
        intersection = list_of_matches[0]
        for i in range(1,len(list_of_matches)):
            tmp_intersection = intersection & list_of_matches[i]
            n_matches = len(list(tmp_intersection))
            if n_matches > 0: #TODO: This assumes some priority list with topic > country > time. Possibly not right.
                intersection = tmp_intersection
            else:
                break
        serializer = BookSerializer(intersection,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
