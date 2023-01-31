
# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only

# Import serializers module from Django REST Framework
from rest_framework import serializers
# Import Custom model
from .models import Book, Topic, Character, Continent, Country, Time, Setting

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

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'topic')

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('id', 'setting')

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'wiki_url','author', 'genre', 'release_date','snippet')

class BookSerializerSettings(serializers.ModelSerializer):
    settings = SettingSerializer(many=True)
    class Meta:
        model = Book
        fields = ('id', 'title', 'wiki_url','author', 'genre', 'release_date','settings','snippet')

class BookSerializerTopics(serializers.ModelSerializer):
    topics = TopicSerializer(many=True)
    class Meta:
        model = Book
        fields = ('id', 'title', 'wiki_url','author', 'genre', 'release_date','topics','snippet')

class BookSerializerCountries(serializers.ModelSerializer):
    countries = CountrySerializer(many=True)
    class Meta:
        model = Book
        fields = ('id', 'title', 'wiki_url','author', 'genre', 'release_date','countries','snippet')

class FullBookSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True)
    settings = SettingSerializer(many=True)
    continents = ContinentSerializer(many=True)
    countries = CountrySerializer(many=True)
    times = TimeSerializer(many=True)
    characters = CharacterSerializer(many=True)
    class Meta:
        model = Book
        fields = ('id', 'title', 'wiki_url','author', 'genre', 'release_date','topics','continents','countries','times','settings','characters','snippet')

