from django.db import models

# Create your models here.
class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Vente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    date_vente = models.DateTimeField(auto_now_add=True)

    def total(self):
        return self.produit.prix * self.quantite
from django.db import models

class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('tmoney', 'Tmoney'),
        ('flooz', 'Flooz'),
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.payment_method} - {self.status}"
