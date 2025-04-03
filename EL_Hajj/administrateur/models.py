from django.db import models
from registration.models import Winners

# Create your models here.


class Vole(models.Model):
    nom = models.CharField(max_length=250)
    aeroprt = models.CharField(max_length=250)
    date_depart = models.DateField()
    heur_depart = models.TimeField()
    date_arrivee = models.DateField()
    heur_arrivee = models.TimeField()
    nb_places = models.IntegerField()
    winner_id = models.ManyToManyField(Winners)
    
    def __str__(self):
        return self.name
    
    
class Hotel(models.Model):
    nom = models.CharField(max_length=250)
    adress = models.CharField(max_length=250)
    winner_id = models.ManyToManyField(Winners)
    
    def __str__(self):
        return self.name
    

    