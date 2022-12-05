from .models import Book, Continent, Country, Time, Character
from .serializers import BookSerializer
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
        serializer = BookSerializer(books,many=True)
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


class GetPaginatedBooksByAgeRange(viewsets.ViewSet):
    def list(self, request, age_range, page):
        start_book = (page - 1) * 100
        books = Book.objects.filter(characters__in=Character.objects.filter(age_range=age_range)).order_by('-release_date')[start_book:start_book + 100]
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
