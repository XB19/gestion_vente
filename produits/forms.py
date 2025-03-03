from django import forms
from .models import Produit
from .models import Vente

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'prix', 'stock']


class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['produit', 'quantite']
