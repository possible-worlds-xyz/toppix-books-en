
# SPDX-FileCopyrightText: Aurelie Herbelot, <aurelie.herbelot@cantab.net> 
#
# SPDX-License-Identifier: AGPL-3.0-only

from django.urls import path, include
from rest_framework import routers
from .views import BookViewSet,GetTopics,GetBooksByTitle,GetPaginatedBooksByContinent,GetPaginatedBooksByCountry,GetPaginatedBooksByTime,GetPaginatedBooksByAgeRange,GetPaginatedBooksByTopic,GetPaginatedBooksBySetting,GetBooksByMultiple
router=routers.DefaultRouter()
router.register('books',BookViewSet)

urlpatterns = [
   path('',include(router.urls)),
   path('books/titles/<str:title>/', GetBooksByTitle.as_view({'get': 'list'})),
   path('topics/', GetTopics.as_view({'get': 'list'})),
   path('books/continent/<str:continent>/<int:page>/', GetPaginatedBooksByContinent.as_view({'get': 'list'})),
   path('books/country/<str:country>/<int:page>/', GetPaginatedBooksByCountry.as_view({'get': 'list'})),
   path('books/time/<str:time>/<int:page>/', GetPaginatedBooksByTime.as_view({'get': 'list'})),
   path('books/topic/<str:topic>/<int:page>/', GetPaginatedBooksByTopic.as_view({'get': 'list'})),
   path('books/setting/<str:setting>/<int:page>/', GetPaginatedBooksBySetting.as_view({'get': 'list'})),
   path('books/agerange/<str:age_range>/<int:page>/', GetPaginatedBooksByAgeRange.as_view({'get': 'list'})),
   path('books/multiple/<str:topic>/<str:country>/<str:time>/', GetBooksByMultiple.as_view({'get': 'list'})),
]

