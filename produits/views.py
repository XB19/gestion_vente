from django.shortcuts import render, redirect, get_object_or_404
from .models import Produit, Categorie, Vente, Payment
from .forms import ProduitForm, VenteForm
from django.db.models import Sum
from django.contrib import messages
import requests
from django.conf import settings
from django.http import JsonResponse

# Ajouter au panier
def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if 'panier' not in request.session:
        request.session['panier'] = {}

    panier = request.session['panier']

    # Vérifier la quantité du produit
    if produit.stock <= 0:
        messages.error(request, f"Le produit {produit.nom} est en rupture de stock.")
        return redirect('liste_produits')

    if str(produit_id) in panier:
        if panier[str(produit_id)]['quantite'] < produit.stock:
            panier[str(produit_id)]['quantite'] += 1
        else:
            messages.error(request, f"Le stock de {produit.nom} est insuffisant pour ajouter au panier.")
            return redirect('liste_produits')
    else:
        panier[str(produit_id)] = {
            'nom': produit.nom,
            'prix': float(produit.prix),
            'quantite': 1
        }

    request.session['panier'] = panier  
    messages.success(request, f"{produit.nom} ajouté au panier !")
    return redirect('payment')



# Base view
def base(request):
    return render(request, 'base.html') 


# Liste des produits
def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'liste.html', {'produits': produits})


# Ajouter un produit
def ajouter_produit(request):
    categories = Categorie.objects.all()

    if request.method == "POST":
        # Affichez le contenu du POST pour vérifier ce qui est envoyé
        print(request.POST)

        nom = request.POST.get("nom")
        categorie_id = request.POST.get("categorie_id")
        prix = request.POST.get("prix")
        quantite = request.POST.get("stock")  # Correction ici : utiliser 'stock' pour cohérence

        # Vérification des champs
        if not (nom and categorie_id and prix and quantite):  # Maintenant, quantite est bien définie
            messages.error(request, "Tous les champs sont requis.")
            return redirect("ajouter_produit")

        try:
            # Validation des données
            prix = float(prix)
            quantite = int(quantite)  # Correction ici : quantite doit être défini avant conversion

            categorie = Categorie.objects.get(id=categorie_id)
            produit = Produit.objects.create(
                nom=nom,
                categorie=categorie,
                prix=prix,
                stock=quantite  # Correction ici : l'attribut 'stock' est utilisé au lieu de 'quantite'
            )
            messages.success(request, f"Produit '{produit.nom}' ajouté avec succès !")
            return redirect("ajouter_produit")
        except Categorie.DoesNotExist:
            messages.error(request, "Catégorie invalide.")
        except ValueError:
            messages.error(request, "Veuillez entrer des valeurs valides pour le prix et la quantité.")

    return render(request, "ajouter_produit.html", {"categories": categories})




# Modifier un produit
def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('liste_produits')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'formulaire_produit.html', {'form': form})


# Supprimer un produit
def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produit.delete()
    return redirect('liste_produits')


# Enregistrer une vente
def enregistrer_vente(request):
    if request.method == "POST":
        # Vérifiez si les clés 'produit_id' et 'vente_id' existent dans request.POST
        produit_id = request.POST.get('produit_id')
        vente_id = request.POST.get('vente_id')

        if not produit_id or not vente_id:
            messages.error(request, "Le produit ou la vente n'a pas été spécifié.")
            return redirect('liste_produits')

        try:
            # Récupérer le produit et la vente
            produit = Produit.objects.get(id=produit_id)
            vente = Vente.objects.get(id=vente_id)

            # Mise à jour du stock du produit
            if vente.quantite > produit.stock:
                messages.error(request, "Stock insuffisant pour cette vente.")
                return redirect('liste_ventes')

            produit.stock -= vente.quantite  # Décrémenter le stock
            produit.save()

            # Enregistrer la vente ou toute autre opération nécessaire
            messages.success(request, f"Vente de {vente.quantite} {produit.nom} effectuée avec succès !")

            # Redirection vers une autre page (par exemple, la liste des ventes)
            return redirect('liste_ventes')
        
        except Produit.DoesNotExist:
            messages.error(request, "Produit non trouvé.")
        except Vente.DoesNotExist:
            messages.error(request, "Vente non trouvée.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
    
    return redirect('liste_produits')  # Rediriger si pas de méthode POST



# Tableau de bord
def tableau_de_bord(request):
    total_produits = Produit.objects.count()
    total_stock = Produit.objects.aggregate(Sum('stock'))['stock__sum'] or 0  # Utiliser "stock" au lieu de "quantite"
    total_ventes = Vente.objects.aggregate(Sum('quantite'))['quantite__sum'] or 0
    revenus_total = Vente.objects.aggregate(Sum('produit__prix'))['produit__prix__sum'] or 0

    ventes_par_jour = Vente.objects.values('date_vente').annotate(total=Sum('quantite'))
    labels = [v['date_vente'].strftime('%d-%m') for v in ventes_par_jour]
    data = [v['total'] for v in ventes_par_jour]

    context = {
        'total_produits': total_produits,
        'total_stock': total_stock,
        'total_ventes': total_ventes,
        'revenus_total': revenus_total,
        'labels': labels,
        'data': data,
    }
    
    return render(request, 'tableau_de_bord.html', context)


# Payment view
def payment_view(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        mode_paiement = request.POST.get('mode_paiement')

        # Assurez-vous que les données sont valides
        if montant and mode_paiement:
            payment = Payment.objects.create(
                montant=montant,
                mode_paiement=mode_paiement
            )
            return render(request, 'payment_success.html', {'payment': payment})
        else:
            return render(request, 'payment_form.html', {'error': 'Données invalides.'})
    return render(request, 'payment_form.html')


# Tmoney payment processing
def process_tmonet_payment(payment):
    url = settings.TMONET_API_URL
    data = {
        'amount': str(payment.amount),
        'order_id': payment.id,
        'callback_url': settings.TMONET_CALLBACK_URL,
    }
    headers = {
        'Authorization': 'Bearer ' + settings.TMONET_API_KEY,
    }
    try:
        api_response = requests.post(url, data=data, headers=headers)
        if api_response.status_code == 200:
            result = api_response.json()
            return {'success': True, 'transaction_id': result.get('transaction_id')}
        else:
            return {'success': False}
    except Exception as e:
        print(f"Erreur Tmonet : {e}")
        return {'success': False}


# Flooz payment processing
def process_flooz_payment(payment):
    url = settings.FLOOZ_API_URL
    data = {
        'amount': str(payment.amount),
        'order_id': payment.id,
        'callback_url': settings.FLOOZ_CALLBACK_URL,
    }
    headers = {
        'Authorization': 'Bearer ' + settings.FLOOZ_API_KEY,
    }
    try:
        api_response = requests.post(url, data=data, headers=headers)
        if api_response.status_code == 200:
            result = api_response.json()
            return {'success': True, 'transaction_id': result.get('transaction_id')}
        else:
            return {'success': False}
    except Exception as e:
        print(f"Erreur Flooz : {e}")
        return {'success': False}
