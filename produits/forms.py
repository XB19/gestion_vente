from django import forms
from .models import Produit, Vente, Payment

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'prix', 'stock']

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['produit', 'quantite']

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        produit = self.cleaned_data.get('produit')
        if quantite > produit.stock:
            raise forms.ValidationError(f"Il n'y a pas assez de stock pour {produit.nom}. Stock disponible : {produit.stock}")
        return quantite

# Ajout de PaymentForm pour le paiement
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['montant', 'mode_paiement']
