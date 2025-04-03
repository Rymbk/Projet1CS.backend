from django.db import models

from django.db import models
from authentication.models import user 
from django.core.exceptions import ValidationError

Nationalities = [
    ('Algérienne', 'Algérien'),
    ('Bahreïnienne', 'Bahreïnien'),
    ('Bangladaise', 'Bangladais'),
    ('Comorienne', 'Comorien'),
    ('Égyptienne', 'Égyptien'),
    ('Émirienne', 'Émirien'),
    ('Indonésienne', 'Indonésien'),
    ('Jordanienne', 'Jordanien'),
    ('Koweïtienne', 'Koweïtien'),
    ('Libanaise', 'Libanais'),
    ('Libyenne', 'Libyen'),
    ('Malaisienne', 'Malaisien'),
    ('Maldivienne', 'Maldivien'),
    ('Malienne', 'Malien'),
    ('Marocaine', 'Marocain'),
    ('Mauritanienne', 'Mauritanien'),
    ('Nigérienne', 'Nigérien'),
    ('Omanaise', 'Omanais'),
    ('Pakistanaise', 'Pakistanais'),
    ('Palestinienne', 'Palestinien'),
    ('Qatarienne', 'Qatarien'),
    ('Saoudienne', 'Saoudien'),
    ('Sénégalaise', 'Sénégalais'),
    ('Somalienne', 'Somalien'),
    ('Soudanaise', 'Soudanais'),
    ('Syrienne', 'Syrien'),
    ('Tchadienne', 'Tchadien'),
    ('Tunisienne', 'Tunisien'),
    ('Turque', 'Turc'),
    ('Yéménite', 'Yéménite')
]


class Haaj(models.Model):
    user = models.OneToOneField(user,  on_delete=models.CASCADE)
    first_name_arabic = models.CharField(max_length=100)
    last_name_arabic = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    NIN = models.CharField(max_length=150, unique=True)
    card_expiration_date = models.DateField()
    passport_id = models.CharField(max_length=100)
    passport_expiration_date = models.DateField()
    nationality = models.CharField(max_length=100, choices=Nationalities)
    phone_number = models.CharField(max_length=20)
    personal_picture = models.ImageField(upload_to='haaj_pictures/')
    maahram_id = models.PositiveIntegerField(null=True , default=None)

    def __str__(self):
        return f'{self.id}'

def save(self, *args, **kwargs):
        if self.user.gender == 'F':      
            if self.maahram_id is None:
                raise ValidationError("Maahram ID is required for female users.")
        
        super(Haaj, self).save(*args, **kwargs)
        
      
        self.user.nombreInscription += 1
        self.user.save()  

class Tirage(models.Model):
    type_tirage=models.IntegerField(default=1)
    nombre_de_place=models.IntegerField(default=0)
    tranche_age=models.IntegerField(default=60, null=True)
    nombre_waiting=models.IntegerField(default=0, null=True)
    tirage_fini=models.BooleanField(default=False)
        
class Baladiya(models.Model):
    name = models.CharField(max_length=100)
    id_utilisateur = models.ManyToManyField(user)
    wilaya=models.IntegerField(null=True,default=None)
    tirage= models.ForeignKey(Tirage,on_delete=models.CASCADE,default=None, null=True,) 
    
    def __str__(self):
        return self.name
      
class Winners(models.Model):
    nin = models.IntegerField(unique=True)
    visite = models.BooleanField(default=None, null=True)
    payement = models.BooleanField(default=None, null=True)

    def __str__(self):
        return str(self.nin)


class WaitingList(models.Model):
    nin = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nin
