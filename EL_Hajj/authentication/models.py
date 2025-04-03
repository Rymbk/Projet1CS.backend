from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from cloudinary.models import CloudinaryField

PROVINCES = [
    (1, 'Wilaya d''Adrar'),
    (2, 'Wilaya de Chlef'),
    (3, 'Wilaya de Laghouat'),
    (4,'Wilaya d''Oum El Bouaghi'),
    (5,'Wilaya de Betna'),
    (6,'Wilaya de Bejaya'),
    (7,'Wilaya de Biskra'),
    (8,'Wilaya de Bechar'),
    (9,'Wilaya de Blida'),
    (10,'Wilaya de Bouira'),
    (11,'Wilaya de Tamanrasset'),
    (12,'Wilaya de Tebessa'),
    (13,'Wilaya de Tlemcen'),
    (14, 'Wilaya de Tiaret'),
    (15,'Wilaya de Tizi Ouzou'),
    (16,'Wilaya d''Alger'),
    (17, 'Wilaya de Djelfa'),
    (18 , 'Wilaya de Jijel'),
    (19,'Wilaya de Setif'),
    (20,'Wilaya de Saida'),
    (21,'Wilaya de Skikda'),
    (22,' Wilaya de SIDI Bel Abbes'),
    (23,'Wilaya de Annaba'),
    (24,'Wilaya de Guelma'),
    (25,'Wilaya de Constantine'),
    (26,'Wilaya de Medea'),
    (27,'Wilaya de Mostaganem'),
    (28,'Wilaya de Msila'),
    (29, 'Wilaya de Mascara'),
    (30, 'Wilaya de Ouargla'),
    (31, 'Wilaya de Oran'),
    (32, 'Wilaya de El Bayadh'),
    (33, 'Wilaya de Illizi'),
    (34, 'Wilaya de Bordj Bou Arreridj'),
    (35, 'Wilaya de Boumerdès'),
    (36, 'Wilaya de El Tarf'),
    (37, 'Wilaya de Tindouf'),
    (38, 'Wilaya de Tissemsilt'),
    (39, 'Wilaya de El Oued'),
    (40, 'Wilaya de Khenchela'),
    (41, 'Wilaya de Souk Ahras'),
    (42, 'Wilaya de Tipaza'),
    (43, 'Wilaya de Mila'),
    (44, 'Wilaya de Aïn Defla'),
    (45, 'Wilaya de Naâma'),
    (46, 'Wilaya de Aïn Témouchent'),
    (47, 'Wilaya de Ghardaïa'),
    (48, 'Wilaya de Relizane'),
    (49, 'Wilaya de El Mghair'),
    (50, 'Wilaya de El Menia'),
    (51, 'Wilaya de Ouled Djellal'),
    (52, 'Wilaya de Bordj Baji Mokhtar'),
    (53, 'Wilaya de Béni Abbès'),
    (54, 'Wilaya de Timimoun'),
    (55, 'Wilaya de Touggourt'),
    (56, 'Wilaya de Djanet'),
    (57, 'Wilaya de In Salah'),
    (58, 'Wilaya de In Guezzam')  
]

roles = [
    ("user","user"),
    ("administrateur","administrateur"),
    ("responsable tirage","responsable tirage"),
    ("medecin","medecin"),
    ("hedj","hedj"),
    ("banquier","banquier"),
]


class userManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
   

class user(AbstractBaseUser):
    username = None
    role = models.CharField(choices=roles)
    email = models.EmailField(max_length=254,unique=True , null=False)
    is_email_verified = models.BooleanField(default=False)
    code = models.CharField(max_length=4, null=True)
    
    
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20,blank=False)
    dateOfBirth = models.DateField(blank=False)
    province = models.IntegerField(choices=PROVINCES)
    city = models.CharField(max_length=200,default="")
    STATUS_CHOICES = [
        ('M', 'male'),
        ('F', 'female'),
    ]
    gender = models.CharField(max_length=1, choices=STATUS_CHOICES, default='M',blank=False)
    view_tirage=models.BooleanField(default=False)
    nombreInscription = models.PositiveSmallIntegerField(default = 0)
    winner=models.BooleanField(default=False)
    winning_date = models.DateField(null=True , default=None)
    personal_picture = CloudinaryField("image", default=None , null = True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=['role','password']
    objects = userManager()

    def __str__(self):
        return self.id

    

class PasswordReset(models.Model):
    objects = models.Manager()
    usere = models.ForeignKey(
        user,
        on_delete=models.CASCADE,
        verbose_name="password reset's user",
        null=True
    )
