from django.urls import path
from django.shortcuts import render
from .views import (
    liste_produits, ajouter_produit, modifier_produit, supprimer_produit,
    enregistrer_vente, tableau_de_bord, payment_view, ajouter_au_panier  # Ajoute ajouter_au_panier ici
)

urlpatterns = [
    path('base/', lambda request: render(request, 'base.html'), name='home'),  
    path('produits/', liste_produits, name='liste_produits'),
    path('produits/ajouter/', ajouter_produit, name='ajouter_produit'),
    path('produits/modifier/<int:produit_id>/', modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:produit_id>/', supprimer_produit, name='supprimer_produit'),
    path('produits/ajouter-au-panier/<int:produit_id>/', ajouter_au_panier, name='ajouter_au_panier'),
    path('vente/', enregistrer_vente, name='enregistrer_vente'),
    path('dashboard/', tableau_de_bord, name='tableau_de_bord'),
    path('payment/', payment_view, name='payment'),
    path('payment/success/', lambda request: render(request, 'payment_success.html'), name='payment_success'),
    path('payment/error/', lambda request: render(request, 'payment_error.html'), name='payment_error'),
]
