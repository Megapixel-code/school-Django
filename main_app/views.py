from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from . import forms
from .tokens import account_activation_token

from . import models

# Create your views here.
def activate_email(request, user, to_email):
    # IMPORTANT, SI LE PROFESSEUR QUI CORRIGE VEUT QUE CETTE FONCTION
    # MARCHE IL DOIT REMPLIR SON PROPRE TOKEN DANS LE FICHIER SUIVANT :
    # "DevWebMaisonConnecte/settings.py"
    # LE PROFFESSEUR DOIT EGALEMENT DECOMMENTER UNE LIGNE DANS LA FONCTION :
    # "register_user"
    mail_subject = "Activation de votre mail"
    messages = render_to_string("activer_mail.html", {
        'user':user.username,
        'domain':get_current_site(request).domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':account_activation_token.make_token(user),
        'protocol':'https' if request.is_secure() else 'http',
    })

    # creating and sending the email
    email = EmailMessage(mail_subject, messages, to=[to_email])
    email.send()


def activate(request, uidb64, token):
    # activating the email once the user clicked on the link in the mail 
    # we sent him4
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Merci d'avoir confirmé vottre email, vous pouvez maintenant vous connecter !")
        return redirect("../../../connexion")
    else:
        messages.error(request, "Lien d'activation Invalide!")

    return redirect('home')


def safe_add_points(request):
    if request.user.is_authenticated:
        user = request.user
        try:
            my_maison_link = models.Link_Maison_User.objects.get(id_user=user)
            my_maison_link.points += 1
            my_maison_link.save()
            return 0
        except models.Link_Maison_User.DoesNotExist:
            return -1



def safe_get_maison_link(request):
    # if the user is not authenticated we redirect to home page
    if not request.user.is_authenticated:
        return -1

    user = request.user
    # otherwise we try to get the link maison user and if the user doesnt have
    # a home we also redirect to home page
    try:
        my_maison_link = models.Link_Maison_User.objects.get(id_user=user)
    except models.Link_Maison_User.DoesNotExist:
        return -1
    
    # if sucessfull return my maison link object
    return my_maison_link



def home(request):
    # if the user is not authenticated we force him to the home page
    if not request.user.is_authenticated:
        return render(request, "home.html", {
            'case':1,
        })

    user = request.user
    # otherwise we try to get the link maison user and if the user doesnt have
    # a home we force him to the home page instead of crashing 
    try:
        my_maison_link = models.Link_Maison_User.objects.get(id_user=user)
    except models.Link_Maison_User.DoesNotExist:
        return render(request, "home.html", {
            'case':2,
        })
    
    safe_add_points(request)

    return render(request, "home.html", {
        'case':3,
    })



def profil(request):
    my_maison_link = safe_get_maison_link(request)
    if my_maison_link == -1:
        return redirect('home')
    my_maison = models.Maison.objects.get(link_maison_user=my_maison_link)

    adresse_maison = my_maison.adresse_maison
    nom_maison = my_maison.nom_maison
    mot_de_passe = my_maison.mot_de_passe

    points = my_maison_link.points
    email_status = my_maison_link.valid_mail

    return render(request, "profil.html", {
        'adresse':adresse_maison,
        'nom':nom_maison,
        'password':mot_de_passe,
        'points':points,
        'email_status':email_status,
    })



def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, ("Mot de passe ou email incorect ..."))
            return render(request, 'authenticate/login.html', {})
    else:
        return render(request, 'authenticate/login.html', {})



def logout_user(request):
    logout(request)
    return redirect('home')



def register_user(request):
    if request.method == "POST":
        form = forms.RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            # activate_email(request, user, form.cleaned_data.get('email'))
            return redirect("home")
    else:
        form = forms.RegisterUserForm()
    return render(request, "authenticate/register.html", {
        'form':form,
    })



def objets(request):
    # changing the db
    if request.method == "POST":
        # change the lamps state
        if request.POST.get("clicked"):
            id_lampe_to_change = request.POST.get("clicked")
            lampe_to_change = models.Lampe.objects.filter(id=id_lampe_to_change)[0]
            if lampe_to_change.etat:
                lampe_to_change.etat = False
            else:
                lampe_to_change.etat = True
            lampe_to_change.save()
        
        # add a object in piece
        elif request.POST.get("piece"):
            id_piece = request.POST.get("piece")
            return redirect(f"ajouter_objet/{id_piece}/")

    # displaying the db
    my_maison_link = safe_get_maison_link(request)
    if my_maison_link == -1:
        return redirect('home')
    my_maison = models.Maison.objects.get(link_maison_user=my_maison_link)
    # list of the user pieces
    list_pieces = models.Piece.objects.filter(id_maison=my_maison)
    
    # get lampes in all of the user pieces
    list_lampes = [[] for _ in list_pieces]
    for i in range(len(list_pieces)):
        lampes_in_piece = models.Lampe.objects.filter(id_piece=list_pieces[i])
        list_lampes[i] = lampes_in_piece

    # combine both to be able to display it
    data = zip(list_pieces, list_lampes)

    return render(request, "objet.html", {
        'data':data,
        'points':my_maison_link.points
    })



def add_objet(request, piece_id):
    piece_to_add_object = models.Piece.objects.filter(id=piece_id)[0]

    # creating the objet
    if request.method == "POST":
        if request.POST.get("submit_new_objet"):
            name_of_new_object = request.POST.get("nom_objet")
            l = models.Lampe(nom_lampe=name_of_new_object, id_piece=piece_to_add_object)
            l.save()
            return redirect("../../../objets/")
    return render(request, "ajouter_un_objet.html")



def add_piece(request):
    if request.method == "POST":
        if request.POST.get("submit_new_piece"):
            name_of_piece = request.POST.get("nom_piece")
            my_maison_link = safe_get_maison_link(request)
            if my_maison_link == -1:
                return redirect('home')
            my_maison = models.Maison.objects.get(link_maison_user=my_maison_link)
            p = models.Piece(id_maison=my_maison, nom_piece=name_of_piece)
            p.save()
            return redirect("../../../objets/")

    return render(request, "ajouter_une_piece.html")



def maison(request):
    return render(request, "maison.html")

def create_maison(request):
    if request.method == "POST":
        if request.POST.get("submit"):
            adresse_maison = request.POST.get("adresse_maison")
            nom_maison = request.POST.get("nom_maison")
            password_maison = request.POST.get("password1")
            password_confirm = request.POST.get("password2")
            if password_confirm == password_maison:
                m = models.Maison(adresse_maison=adresse_maison, mot_de_passe=password_maison, nom_maison=nom_maison)
                l_m_u = models.Link_Maison_User(id_maison=m, id_user=request.user)
                m.save()
                l_m_u.save()
                return redirect("../../../objets/")
            else:
                return render(request, "cree_maison.html", {
                    'case':1,
                })

    return render(request, "cree_maison.html", {
        'case':0,
    })

def join_maison(request):
    list_maisons = []

    if request.method == "POST":
        id_maison_to_add = request.POST.get("submit_rejoindre")
        if request.POST.get("submit_search"):
            query = request.POST.get("adresse_maison")
            list_maisons = models.Maison.objects.filter(adresse_maison__contains=query)
        elif id_maison_to_add:
            password = request.POST.get("mot_de_passe")
            print(password, id_maison_to_add)
            maison_to_add = models.Maison.objects.filter(id=id_maison_to_add)[0]
            print(maison_to_add)
            if maison_to_add.mot_de_passe == password:
                l_m_u = models.Link_Maison_User(id_maison=maison_to_add, id_user=request.user)
                l_m_u.save()
                return redirect("../../../objets/")
            else:
                messages.success(request, ("Mot de passe incorect ..."))
    
    
    return render(request, "rejoindre_maison.html", {
        'list_maisons':list_maisons
    })

def a_propos_de_nous(request):
    return render(request, "A_propos_de_nous.html")

def contact(request):
    return render(request, "Contact.html")