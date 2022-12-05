from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=100, null=True, blank=False)
    wiki_url = models.URLField(max_length=300, unique=True, null=True, blank=False)
    release_date = models.IntegerField(null=True,blank=False)
    snippet = models.TextField(null=True,blank=False)
    female_lead = models.CharField(max_length=1, null=True, blank=False)

class Character(models.Model):

    NONBINARY = 'N'
    FEMALE = 'F'
    MALE = 'M'
    UNKNOWN = 'U'
    GENDER_CHOICES = [
        (NONBINARY, 'Non-binary'),
        (FEMALE, 'Female'),
        (MALE, 'Male'),
        (UNKNOWN, 'Unknown'),
    ]

    KID = "KI"
    TEEN = "TE"
    YOUNG_ADULT= "YA"
    ADULT = "AD"
    EARLY_SENIOR= "ES"
    OLDER_SENIOR = "OS"
    OLD = "OL"
    AGE_CHOICES = [
        (KID, "Kid"),
        (TEEN, "Teen"),
        (YOUNG_ADULT, "Young Adult"),
        (ADULT, "Adult"),
        (EARLY_SENIOR, "Early Senior"),
        (OLDER_SENIOR, "Older Senior"),
        (OLD, "Old"),
    ]
        
    name = models.CharField(max_length=50, null=True, blank=False)
    gender = models.CharField(max_length=1, choices = GENDER_CHOICES, default=FEMALE)
    age = models.IntegerField(null=True,blank=False)
    age_range = models.CharField(max_length=2,choices = AGE_CHOICES, default=ADULT)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='characters',blank=True,null=True) 
    #book = models.ManyToManyField(Book, related_name='characters',blank=True) 

class Country(models.Model):
    country = models.CharField(max_length=50, null=True, blank=False)
    books = models.ManyToManyField(Book, related_name='countries',blank=True) 

class Continent(models.Model):

    AFRICA = 'AF'
    ANTARCTICA = 'AN'
    ASIA = 'AS'
    OCEANIA = 'OZ'
    EUROPE = 'EU'
    SOUTHAMERICA = 'SA'
    NORTHAMERICA = 'NA'
    ELSEWHERE = 'EL'
    UNKNOWN = 'UN'
    CONTINENT_CHOICES = [
        (AFRICA, 'Africa'),
        (ANTARCTICA, 'Antarctica'),
        (ASIA, 'Asia'),
        (OCEANIA, 'Oceania'),
        (EUROPE, 'Europe'),
        (SOUTHAMERICA, 'South America'),
        (NORTHAMERICA, 'North America'),
        (ELSEWHERE, 'Elsewhere'),
        (UNKNOWN, 'Unknown')
    ]

    continent = models.CharField(max_length=2, choices = CONTINENT_CHOICES, default=UNKNOWN, blank=False)
    books = models.ManyToManyField(Book, related_name='continents',blank=True) 

class Time(models.Model):
    rangeStart = models.IntegerField(null=True)
    rangeEnd = models.IntegerField(null=True)
    books = models.ManyToManyField(Book, related_name='times', blank=True) 
