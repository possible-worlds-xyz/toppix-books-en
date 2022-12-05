# Import serializers module from Django REST Framework
from rest_framework import serializers
# Import Custom model
from .models import Book, Character, Continent, Country, Time

class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = ('id', 'continent')

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'country')


class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = ('id', 'rangeStart', 'rangeEnd')

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ('id', 'name', 'age', 'age_range','gender')

class BookSerializer(serializers.ModelSerializer):
    continents = ContinentSerializer(many=True)
    countries = CountrySerializer(many=True)
    times = TimeSerializer(many=True)
    characters = CharacterSerializer(many=True)
    class Meta:
        model = Book
        fields = ('id', 'title', 'wiki_url','release_date','female_lead','continents','countries','times','characters','snippet')


