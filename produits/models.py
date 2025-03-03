from django.db import models  

class Utilisateur(models.Model):  
    nom = models.CharField(max_length=100)  
    role = models.CharField(max_length=50)    

class Categorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()  

    def __str__(self):
        return self.nom

    def __str__(self):  
        return self.nom  

class Client(models.Model):  
    nom = models.CharField(max_length=100)  
    prenom = models.CharField(max_length=100)  
    numero = models.IntegerField()  


    def __str__(self):  
        return f"{self.prenom} {self.nom}"  

class Vente(models.Model):  
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)  
    quantite = models.PositiveIntegerField()  
    date_vente = models.DateTimeField(auto_now_add=True)  


    def __str__(self):  
        return f"Vente de {self.produit.nom} - Quantité: {self.quantite}"  

class Payment(models.Model):  
    PAYMENT_CHOICES = (  
        ('tmoney', 'Tmoney'),  
        ('flooz', 'Flooz'),  
    )  
    montant = models.DecimalField(max_digits=10, decimal_places=2)  
    mode_paiement = models.CharField(max_length=20, choices=PAYMENT_CHOICES)  
    date_paiement = models.DateTimeField(auto_now_add=True)  

    def __str__(self):  
        return f"Payment #{self.id} - {self.mode_paiement} - Montant: {self.montant}"  