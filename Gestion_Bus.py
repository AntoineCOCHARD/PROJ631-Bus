# -*- coding: utf-8 -*-

import copy as cp

data_file_names = ['1_Poisy-ParcDesGlaisins.txt','2_Piscine-Patinoire_Campus.txt','3_Altais_Novel.txt','4_Seynod-Neigeos_Campus.txt']
liste_arrets=set()  # ensemble plutôt que liste pour gérer les doublons plus naturellement
liste_trajets=[]
periode='reg'

class Arret():
    
    def __init__(self, nom, lignes):
        self.nom = nom
        self.lignes = lignes
    
    def get_lignes(self):
        return self.lignes
    
    def get_nom(self):
        return(self.nom)
        
    def set_ligne(self,ligne):
        self.lignes.append(ligne)
    

class Trajet() :
    
    def __init__(self,dep,arr,liste_hor,ligne,periode='reg') :
        self.dep = dep
        self.arr = arr
        self.liste_hor = liste_hor
        self.ligne=ligne
    
    def proch_dep(self,horaire):
        num=0
        while not ordre(horaire,self.liste_hor[num][0]) :
            num +=1
        return self.liste_hor[num]
    
    def get_dep(self):
        return self.dep
    
    def get_arr(self):
        return self.arr
    
    def get_ligne(self):
        return self.ligne
    
    def get_per(self):
        return self.periode

    def set_hor(self,horaire):
        self.liste_hor.append(horaire)
        
    def get_hor(self):
        return self.liste_hor
        
def duree(t1,t2) :
    """prend en arguments deux horaires sous la forme "hh:mm" ou "h:mm"
    renvoie l'écart
    le premier est antérieur au second,
    le changement de jour n'est pas pris en charge"""
    h1,m1=[int(ch) for ch in (t1.split(":"))]
    h2,m2=[int(ch) for ch in (t2.split(":"))]
    return (h2-h1)*60+m2-m1

def ordre(t1,t2) :
    """ prend en arguments deux horaires sous la forme "hh:mm" ou "h:mm"
    renvoie True si t1 est antérieur à t2, False sinon"""
    h1,m1=[int(ch) for ch in (t1.split(":"))]
    h2,m2=[int(ch) for ch in (t2.split(":"))]
    if h1>h2 or (h1==h2 and m1>m2) :
        return False
    else :
        return True

def dates2dic(dates):
    dic = {}
    splitted_dates = dates.split("\n")
    #print(splitted_dates)
    for stop_dates in splitted_dates:
        tmp = stop_dates.split(" ")
        dic[tmp[0]] = tmp[1:]
    return dic

def ouvre(fichier) :
    try:
        with open(fichier, 'r', encoding="utf-8") as f:
            content = f.read()
    except OSError:
        # 'File not found' error message.
        print("File not found")
        
    splitted_content = content.split("\n\n")
    regular_path = splitted_content[0].split(' N ')
    regular_date_go = dates2dic(splitted_content[1])
    regular_date_back = dates2dic(splitted_content[2])
    
    we_holidays_path = splitted_content[3].split(' N ')
    we_holidays_date_go = dates2dic(splitted_content[4])
    we_holidays_date_back = dates2dic(splitted_content[5])
    
    
    return regular_path,regular_date_go,regular_date_back,we_holidays_path,we_holidays_date_go,we_holidays_date_back

def arret_de_nom(lieu):
    '''Fonction qui vérifie s'il existe un arrêt avec le nom donné
    en argument dans le réseau'''
    for arret in liste_arrets :
        if arret.get_nom()==lieu :
            return arret
    raise NameError("Pas d'arrêt de ce nom")

def affiche_it(itin):
    ''' Fonction qui affiche un itinéraire donné en argument puis affiche 
    son nombre d'arrêts et ses temps de bus et d'attente '''
    print()
    duree_tot = 0 
    for elt in itin :
        duree_tot += duree(elt[1],elt[2])
        print(elt[0].get_nom().center(30)," arrivée à ",elt[2])
    print("Le nombres d'arrets de ce trajet est : ",len(itin))
    print("Durée totale de bus pour ce tajet : ", duree_tot, "min")
    temps_pause=(duree(itin[0][1],itin[-1][2])-duree_tot)
    print("Le temps d'attente avant et entre les bus est de : ",temps_pause, "min")
    print()

# ---------- Parcours de graphe ---------- #

def itineraire(depart,destination,liste_etapes,l_itin_possibles):
    """ Fonction récursive qui prend en arguments deux arrets, 
    une liste de listes formées des arrets-étapes et heures de départ 
    et enfin la liste des itinéraires possibles""" 
    for traj in [tr for tr in liste_trajets if tr.dep==depart] :
        l_e = cp.deepcopy(liste_etapes)
        #Test pour sortir d'une éventuelle boucle infinie
        if len(l_e)>50 :
            break
        #On vérifie ici que l'arrêt d'arrivée n'a pas deja été visité
        if traj.arr.get_nom() not in [stop[0].get_nom() for stop in l_e]:
            heure_dep,heure_arr=traj.proch_dep(l_e[-1][-1]) 
            # le dernier élément de l_e contient l'arret présent et l'heure d'arrivée dans cet arret
            l_e.append([traj.arr,heure_dep,heure_arr])
            if traj.arr == destination :
                l_itin_possibles.append(l_e)
                return l_e,l_itin_possibles
            else :
                #Appel récurisif de la fonction pour continuer à partir de l'arret présent
                itineraire(traj.arr,destination,l_e,l_itin_possibles)

def trajet_au_plus_court(l_itin_possibles):
    """ Fonction qui prend en argument une liste d'itinéraires
    et qui renvoie l'affichage de la solution avec le moins d'arrêts"""
    traj_plus_court=[0]
    mini=100
    for k in range(len(l_itin_possibles)):
        if len(l_itin_possibles[k]) < mini:
            mini = len(l_itin_possibles[k])
            traj_plus_court=l_itin_possibles[k]
    return affiche_it(traj_plus_court)


def trajet_arrive_le_plus_tot(l_itin_possibles):
    """ Fonction qui prend en argument une liste d'itinéraires
    et qui renvoie l'affichage de la solution avec l'heure d'arrivée 
    la plus proche du départ """
    traj_plus_tot=l_itin_possibles[0]
    heure_mini=l_itin_possibles[0][-1][-1]
    for k in range(len(l_itin_possibles)):
        if ordre(l_itin_possibles[k][-1][-1],heure_mini):
            heure_mini=l_itin_possibles[k][-1][-1]
            traj_plus_tot=l_itin_possibles[k]
    return affiche_it(traj_plus_tot)

def trajet_le_plus_rapide(l_itin_possibles):
    """ Fonction qui prend en argument une liste d'itinéraires
    et qui renvoie l'affichage de la solution avec le moins de temps de bus"""
    traj_plus_rapide=l_itin_possibles[0]
    temps=duree(l_itin_possibles[0][1][-2],l_itin_possibles[0][-1][-1])
    for k in range(len(l_itin_possibles)):
        if duree(l_itin_possibles[k][1][-2],l_itin_possibles[k][-1][-1]) < temps:
            temps = duree(l_itin_possibles[k][1][-2],l_itin_possibles[k][-1][-1])
            traj_plus_rapide=l_itin_possibles[k]
    return affiche_it(traj_plus_rapide)

# ---------- PROGRAMME PRINCIPAL ---------- #

# ---------- Intégration des données ---------- #        
for fichier in data_file_names :
    num_ligne=fichier[0]
    r_p,r_d_g,r_d_b,w_p,w_d_g,w_d_b = ouvre(fichier)
    for lieu in r_d_g.keys() :
        if lieu not in [arr.nom for arr in liste_arrets] :
            #print('ajout de ',lieu)
            ar = Arret(lieu,[num_ligne])
            liste_arrets.add(ar)
        else :
            #print('pas ajout de ',lieu)
            for a in liste_arrets :
                if a.nom == lieu :
                    a.set_ligne(num_ligne)
                    
    '''Création des trajets et remplissage des horaires associés'''
    if num_ligne == '1' :
        #print('-----------ligne 1----------')
        # ligne 1 aller
        for lieu in r_p[0].split(" + "):
            arret=arret_de_nom(lieu)
            traj=Trajet(arret,arret_de_nom(r_p[1]),[],'1g')
            liste_trajets.append(traj)
        for i in range(1,len(r_p)-1):
            traj=Trajet(arret_de_nom(r_p[i]),arret_de_nom(r_p[i+1]),[],'1g')
            liste_trajets.append(traj)
        for traj in liste_trajets :
            for i in range(len(r_d_g[traj.get_dep().get_nom()])) :
                if r_d_g[traj.get_dep().get_nom()][i] !='-' and r_d_g[traj.get_arr().get_nom()][i] !='-':
                    traj.set_hor([r_d_g[traj.get_dep().get_nom()][i],r_d_g[traj.get_arr().get_nom()][i]])
        l1=len(liste_trajets)
        # ligne 1 retour
        for i in range(1,len(r_p)-1):
            traj=Trajet(arret_de_nom(r_p[i+1]),arret_de_nom(r_p[i]),[],'1b')
            liste_trajets.append(traj)
        for lieu in r_p[0].split(" + "):
            traj=Trajet(arret_de_nom(r_p[1]),arret_de_nom(lieu),[],'1b')
            liste_trajets.append(traj)
        for traj in liste_trajets[l1:] :
            for i in range(len(r_d_g[traj.get_dep().get_nom()])) :
                if r_d_b[traj.get_dep().get_nom()][i] !='-' and r_d_b[traj.get_arr().get_nom()][i] !='-' :
                    traj.set_hor([r_d_b[traj.get_dep().get_nom()][i],r_d_b[traj.get_arr().get_nom()][i]])
        l1=len(liste_trajets)
    else :
        #print('-----------ligne 2----------')
        # ligne 2 (ou plus...) aller
        for i in range(len(r_p)-1):
            traj=Trajet(arret_de_nom(r_p[i]),arret_de_nom(r_p[i+1]),[],num_ligne+'g')
            liste_trajets.append(traj)
        for traj in liste_trajets[l1:] :
            for i in range(len(r_d_g[traj.get_dep().get_nom()])) :
                #print(traj.dep,i)
                if r_d_g[traj.get_dep().get_nom()][i] !='-' and r_d_g[traj.get_arr().get_nom()][i] !='-' :
                    traj.set_hor([r_d_g[traj.get_dep().get_nom()][i],r_d_g[traj.get_arr().get_nom()][i]])
        l1=len(liste_trajets)
        # ligne 2 (ou plus...) retour
        for i in range(len(r_p)-1):
            traj=Trajet(arret_de_nom(r_p[i+1]),arret_de_nom(r_p[i]),[],num_ligne+'b')
            liste_trajets.append(traj)     
        for traj in liste_trajets[l1:] :
            for i in range(len(r_d_b[traj.get_dep().get_nom()])) :
                if r_d_b[traj.get_dep().get_nom()][i] !='-' and r_d_b[traj.get_arr().get_nom()][i] !='-' :
                    traj.set_hor([r_d_b[traj.get_dep().get_nom()][i],r_d_b[traj.get_arr().get_nom()][i]])
        l1=len(liste_trajets)
                    

# ---------- Instanciation du problème ---------- #
print("les arrêts disponibles sont : ")
print([arr.nom for arr in liste_arrets])    
nom_dep = input("arret de départ ? ")
while nom_dep not in [arr.nom for arr in liste_arrets]:
    print("les arrêts disponibles sont : ")
    print([arr.nom for arr in liste_arrets])
    nom_dep = input("arret de départ ? ")
    
nom_dest = input("arret de destination ? ")
while nom_dest not in [arr.nom for arr in liste_arrets]:
    print("les arrêts disponibles sont : ")
    print([arr.nom for arr in liste_arrets])
    nom_dest = input("arret de destination ? ")
    
heure=input("Quelle heure est-il ? hh:mm ")
                    
arret_depart=[arr for arr in liste_arrets if arr.nom==nom_dep][0]
arret_destination=[arr for arr in liste_arrets if arr.nom==nom_dest][0]

l_itin_possibles=[]
a = itineraire(arret_depart,arret_destination,[[arret_depart,heure,heure]],l_itin_possibles)


print("-----------Trajet au plus court (Shortest) :")
trajet_au_plus_court(l_itin_possibles)
print("-----------Trajet qui arrive le plus tôt (Foremost) :")
trajet_arrive_le_plus_tot(l_itin_possibles)
print("-----------Trajet le plus rapide (Fastest) :")
trajet_le_plus_rapide(l_itin_possibles)
