from django.urls import path, include
from rest_framework import routers
from .views import BookViewSet,GetBooksByTitle,GetBooksByFemaleLead,GetPaginatedBooksByFemaleLead,GetBooksByContinent,GetPaginatedBooksByContinent,GetBooksByCountry,GetPaginatedBooksByCountry,GetPaginatedBooksByTime,GetPaginatedBooksByAgeRange

router=routers.DefaultRouter()
router.register('books',BookViewSet)

urlpatterns = [
   path('',include(router.urls)),
   path('books/titles/<str:title>/', GetBooksByTitle.as_view({'get': 'list'})),
   path('books/femalelead/<str:female_lead>/', GetBooksByFemaleLead.as_view({'get': 'list'})),
   path('books/femalelead/<str:female_lead>/<int:page>/', GetPaginatedBooksByFemaleLead.as_view({'get': 'list'})),
   path('books/continent/<str:continent>/', GetBooksByContinent.as_view({'get': 'list'})),
   path('books/continent/<str:continent>/<int:page>/', GetPaginatedBooksByContinent.as_view({'get': 'list'})),
   path('books/country/<str:country>/', GetBooksByCountry.as_view({'get': 'list'})),
   path('books/country/<str:country>/<int:page>/', GetPaginatedBooksByCountry.as_view({'get': 'list'})),
   path('books/time/<str:time>/<int:page>/', GetPaginatedBooksByTime.as_view({'get': 'list'})),
   path('books/agerange/<str:age_range>/<int:page>/', GetPaginatedBooksByAgeRange.as_view({'get': 'list'})),
]

