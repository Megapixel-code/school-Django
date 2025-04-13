from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
# python manage.py makemigrations
# python manage.py migrate

class Maison(models.Model):
    adresse_maison = models.CharField(max_length=200)
    nom_maison = models.CharField(max_length=100)
    mot_de_passe = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nom_maison} {self.adresse_maison} {self.mot_de_passe}"
    
class Link_Maison_User(models.Model):
    id_maison = models.OneToOneField(Maison, on_delete=models.CASCADE, primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    valid_mail = models.BooleanField(default=False)
    points = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id_maison", "id_user"], name="unique_ids"
            )
        ]

    def __str__(self):
        return f"{self.id_maison} {self.id_user} {self.valid_mail} {self.points}"

class Piece(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    id_maison = models.ForeignKey(Maison, on_delete=models.CASCADE)
    nom_piece = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nom_piece} {self.id_maison}"

class Lampe(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    id_piece = models.ForeignKey(Piece, on_delete=models.CASCADE)
    etat = models.BooleanField(default=False)
    nom_lampe = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.etat} {self.nom_lampe} {self.id_piece}"

