from django.urls import path
from django.shortcuts import render
from .views import (
    liste_produits, ajouter_produit, modifier_produit, supprimer_produit,
    enregistrer_vente, tableau_de_bord, payment_view, ajouter_au_panier, 
    payment_success_view, payment_error_view  # Importer les vues pour success et error
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
    path('payment/success/', payment_success_view, name='payment_success'),  # Vue dédiée pour success
    path('payment/error/', payment_error_view, name='payment_error'),  # Vue dédiée pour error
]
