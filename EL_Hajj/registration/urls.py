from django.urls import path
from .views import check_tirage_definition, fetch_winners, participants_tirage, registration,associate_tirage_with_baladiyas,baladiya_names_by_utilisateur,tirage_défini,winners_by_baladiya,visite_status,view_tirage
from . import views
urlpatterns = [
    path('registration', registration, name='registration'),
    path('fetch-winners/', fetch_winners, name='fetch_winners'),
    path('baladiya_names_by_utilisateur/', baladiya_names_by_utilisateur, name='baladiya_names_by_utilisateur'),
    path('associate-tirage', associate_tirage_with_baladiyas, name='associate_tirage_with_baladiyas'),
    path('tirage_défini/', tirage_défini, name='tirage_fini'),
    path('winners_by_baladiya/', winners_by_baladiya, name='winners_by_baladiya'),
    path('visite_status/', visite_status, name='visite_status'),
    path('winners_accepted/',views.winners_accepted, name='winners_accepted'),
    path('payment_status/',views.payment_status, name='payment_status'),
    path('participants_tirage/', participants_tirage, name='participants_tirage'),
    path('check-tirage/', check_tirage_definition, name='check_tirage_definition'),
    path('view_tirage/', view_tirage, name='view_tirage'),
  
]
