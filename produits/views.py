from django.shortcuts import render
from .models import Produit
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produit
from .forms import ProduitForm
from .models import Vente
from .forms import VenteForm
from django.db.models import Sum
from django.shortcuts import render
from .models import Produit, Vente
import requests
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Payment
from .models import Produit, Categorie
from django.http import JsonResponse
from django.contrib import messages


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Produit

def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if 'panier' not in request.session:
        request.session['panier'] = {}

    panier = request.session['panier']

    if str(produit_id) in panier:
        panier[str(produit_id)]['quantite'] += 1
    else:
        panier[str(produit_id)] = {
            'nom': produit.nom,
            'prix': float(produit.prix),  
            'quantite': 1
        }

    request.session['panier'] = panier  
    messages.success(request, f"{produit.nom} ajouté au panier !")

    return redirect('payment')



def base(request):
    return render(request, 'base.html') 

def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'liste.html', {'produits': produits})

def ajouter_produit(request):
    categories = Categorie.objects.all()  

    if request.method == "POST":
        nom = request.POST.get("nom")
        categorie_id = request.POST.get("categorie_id")
        prix = request.POST.get("prix")
        stock = request.POST.get("stock")

        if not (nom and categorie_id and prix and stock):
            messages.error(request, "Tous les champs sont requis.")
            return redirect("ajouter_produit")

        try:
            categorie = Categorie.objects.get(id=categorie_id)
            produit = Produit.objects.create(
                nom=nom,
                categorie=categorie,
                prix=float(prix),
                stock=int(stock)
            )
            messages.success(request, f"Produit '{produit.nom}' ajouté avec succès !")
            return redirect("ajouter_produit")
        except Categorie.DoesNotExist:
            messages.error(request, "Catégorie invalide.")
        except ValueError:
            messages.error(request, "Veuillez entrer des valeurs valides pour le prix et le stock.")

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

def enregistrer_vente(request):
    if request.method == "POST":
        form = VenteForm(request.POST)
        if form.is_valid():
            vente = form.save()
            produit = vente.produit
            produit.stock -= vente.quantite
            produit.save()
            return redirect('liste_produits')
    else:
        form = VenteForm()
    return render(request, 'formulaire_vente.html', {'form': form})


def tableau_de_bord(request):
    total_produits = Produit.objects.count()
    total_stock = Produit.objects.aggregate(Sum('stock'))['stock__sum'] or 0
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



def payment_view(request):
    panier = request.session.get('panier', {})  # Récupérer le panier depuis la session

    total_amount = sum(item['prix'] * item['quantite'] for item in panier.values())

    if request.method == 'POST':
        amount = request.POST.get('amount', total_amount)  # Utiliser le montant total du panier
        payment_method = request.POST.get('payment_method')

        payment = Payment.objects.create(
            amount=amount,
            payment_method=payment_method
        )

        if payment_method == 'tmoney':
            response = process_tmonet_payment(payment)
        elif payment_method == 'flooz':
            response = process_flooz_payment(payment)
        else:
            response = {'success': False}

        if response.get('success'):
            payment.transaction_id = response.get('transaction_id')
            payment.status = 'completed'
            payment.save()
            return redirect('payment_success')
        else:
            payment.status = 'failed'
            payment.save()
            return redirect('payment_error')

    return render(request, 'payment_form.html', {'panier': panier, 'total_amount': total_amount})


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

