# -*- coding: utf-8 -*-
import os,os.path
import sys
import random
from helper import Helper as hlp
import math

""" ORION EMPIRE ******************

VERSION 01
- changer controleur.prochaintour pour appliquer la suggestion de Miguel - FAIT !
- taille de la map - FAIT !
    et canvas size  - FAIT !
    et scrollbar - FAIT !
- taille 8000x8000  - FAIT
- 200 etoiles  - FAIT

VERSION 02
-  Minimap  - FAIT
    et clickable  - FAIT

VERSION 03
- Vision systeme solaire
    - changer cadrejeu pour cadregalactique - FAIT !
    - changer Systeme et systeme pour Systeme et systeme - FAIT !
    
VERSION 04-10
- construction des cadres de base - Refactoring
- rapporter les modes en objets inbdependants pour .la representation
    - ajout planetes autour de systeme
    - creer cadresysteme 
    - boutons niveaux dans info, au dessus de minimap
        NOTE ces boutons sont pour le developement SEULEMENT
             les changements de niveaux se feront en game play
    - choisir cadresysteme, le bouton
    - changer vision pour cadresysteme
    - revenir a cadregalactique
    
- Modifier minimap
    - ajouter visualisation d'effectifs  vaisseaux, autres ???


"""

modeauto=3

class Id():
    id=0
    def prochainid():
        Id.id+=1
        str_id="id_"+str(Id.id)
        return str_id # Id.id


class Pulsar():
    def __init__(self,x,y):
        self.id=Id.prochainid()
        self.proprietaire="inconnu"
        self.x=x
        self.y=y
        self.periode=random.randrange(20,50,5)
        self.moment=0
        self.phase=1 
        self.mintaille=self.taille=random.randrange(2,4)
        self.maxtaille=self.mintaille++random.randrange(1,3)
        self.pas=self.maxtaille/self.periode
        self.taille=self.mintaille
        
    def evoluer(self):
        self.moment=self.moment+self.phase
        if self.moment==0:
            self.taille=self.mintaille
            self.phase=1
        elif self.moment==self.periode:
            self.taille=self.mintaille+self.maxtaille
            self.phase=-1
        else:
            self.taille=self.mintaille+(self.moment*self.pas)
 
class Ville():
    def __init__(self,parent,proprio="inconnu",x=2500,y=2500):
        self.id=Id.prochainid()
        self.parent=parent
        self.x=x
        self.y=y
        self.proprietaire=proprio
        self.taille=20
               
class Mine():
    def __init__(self,parent,nom,systemeid,planeteid,x,y):
        self.id=Id.prochainid()
        self.parent=parent
        self.x=x
        self.y=y
        self.systemeid=systemeid
        self.planeteid=planeteid
        self.entrepot=0
                
class Planete():
    def __init__(self,parent,type,dist,taille,angle):
        self.id=Id.prochainid()
        self.parent=parent
        self.posXatterrissage=random.randrange(5000)
        self.posYatterrissage=random.randrange(5000)
        self.infrastructures=[Ville(self)]
        self.proprietaire="inconnu"
        self.visiteurs={}
        self.distance=dist
        self.type=type
        self.taille=taille
        self.angle=angle
        
class Etoile():
    def __init__(self,parent,x,y):
        self.id=Id.prochainid()
        self.parent=parent
        self.type=random.choice(["rouge","rouge","rouge",
                                 "jaune","jaune",
                                 "bleu"])
        self.taille=random.randrange(25)/10 +0.1   # en masse solaire
        
class Systeme():
    def __init__(self,x,y):
        self.id=Id.prochainid()
        self.proprietaire="inconnu"
        self.visiteurs={}
        self.diametre=50 # UA unite astronomique = 150000000km
        self.x=x
        self.y=y
        self.etoile=Etoile(self,x,y)
        self.planetes=[]
        self.planetesvisites=[]
        self.creerplanetes()
        
    def creerplanetes(self):
        systemeplanetaire=random.randrange(5) # 4 chance sur 5 d'avoir des planetes
        if systemeplanetaire:
            nbplanetes=random.randrange(12)+1
            for i in range(nbplanetes):
                type=random.choice(["roc","gaz","glace"])
                distsol=random.randrange(250)/10 #distance en unite astronomique 150000000km
                taille=random.randrange(50)/100 # en masse solaire
                angle=random.randrange(360)
                self.planetes.append(Planete(self,type,distsol,taille,angle))
                
class Vaisseau():
    def __init__(self,nom,systeme):
        self.id=Id.prochainid()
        self.proprietaire=nom
        self.taille=16
        self.base=systeme
        self.angletrajet=0
        self.angleinverse=0
        self.x=self.base.x
        self.y=self.base.y
        self.taille=16
        self.cargo=0
        self.energie=100
        self.vitesse=random.choice([0.001,0.003,0.005,0.01])*5 #0.5
        self.cible=None 
        
    def avancer(self):
        rep=None
        if self.cible:
            x=self.cible.x
            y=self.cible.y
            self.x,self.y=hlp.getAngledPoint(self.angletrajet,self.vitesse,self.x,self.y)
            if hlp.calcDistance(self.x,self.y,x,y) <=self.vitesse:
                rep=self.cible
                self.base=self.cible
                self.cible=None
            return rep
        
    def ciblerdestination(self,p):
        self.cible=p
        self.angletrajet=hlp.calcAngle(self.x,self.y,p.x,p.y)
        self.angleinverse=math.radians(math.degrees(self.angletrajet)+180)
        dist=hlp.calcDistance(self.x,self.y,p.x,p.y)
        #print("Distance",dist," en ", int(dist/self.vitesse))
    
class Joueur():
    def __init__(self,parent,nom,systemeorigine,couleur):
        self.id=Id.prochainid()
        self.parent=parent
        self.nom=nom
        self.systemeorigine=systemeorigine
        self.couleur=couleur
        self.systemesvisites=[systemeorigine]
        self.vaisseauxinterstellaires=[]
        self.vaisseauxinterplanetaires=[]
        self.actions={"creervaisseau":self.creervaisseau,
                      "ciblerdestination":self.ciblerdestination,
                      "atterrirplanete":self.atterrirplanete,
                      "visitersysteme":self.visitersysteme,
                      "creermine":self.creermine}
        
    def creermine(self,listeparams):
        nom,systemeid,planeteid,x,y=listeparams
        for i in self.systemesvisites:
            if i.id==systemeid:
                for j in i.planetes:
                    if j.id==planeteid:
                        mine=Mine(self,nom,systemeid,planeteid,x,y)
                        j.infrastructures.append(mine)
                        self.parent.parent.affichermine(nom,systemeid,planeteid,x,y)
                        
        
        
                
    def atterrirplanete(self,d):
        nom,systeid,planeid=d
        for i in self.systemesvisites:
            if i.id==systeid:
                for j in i.planetes:
                    if j.id==planeid:
                        i.planetesvisites.append(j)
                        if nom==self.parent.parent.monnom:
                            self.parent.parent.voirplanete(i.id,j.id)
                        return 1
        
    
    def visitersysteme(self,systeme_id):
        for i in self.parent.systemes:
            if i.id==systeme_id:
                self.systemesvisites.append(i)
                
    def creervaisseau(self,id):
        for i in self.systemesvisites:
            if i.id==id:
                v=Vaisseau(self.nom,i)
                self.vaisseauxinterstellaires.append(v)
                return 1
        
    def ciblerdestination(self,ids):
        idori,iddesti=ids
        for i in self.vaisseauxinterstellaires:
            if i.id== idori:
                for j in self.parent.systemes:
                    if j.id== iddesti:
                        #i.cible=j
                        i.ciblerdestination(j)
                        return
                for j in self.systemesvisites:
                    if j.id== iddesti:
                        #i.cible=j
                        i.ciblerdestination(j)
                        return
        
    def prochaineaction(self): # NOTE : cette fonction sera au coeur de votre developpement
        global modeauto
        for i in self.vaisseauxinterstellaires:
            if i.cible:
                rep=i.avancer()
                if rep:
                    if rep.proprietaire=="inconnu":
                        rep.proprietaire=self.nom
                        if rep not in self.systemesvisites:
                            self.systemesvisites.append(rep)
                            self.parent.changerproprietaire(self.nom,self.couleur,rep)
            
            elif modeauto:
                p=random.choice(self.parent.systemes)
                i.ciblerdestination(p)
                
        if len(self.vaisseauxinterstellaires)<modeauto:
            print("DEMANDE AUTO ",self.parent.parent.cadre,self.nom,len(self.vaisseauxinterstellaires))
            self.creervaisseau(str(self.systemeorigine.id))   
    
class Modele():
    def __init__(self,parent,joueurs,dd):
        self.parent=parent
        self.diametre,self.densitestellaire=dd
        self.nbsystemes=int(self.diametre**2/self.densitestellaire)
        print(self.nbsystemes)
        
        self.joueurs={}
        self.joueurscles=joueurs
        self.actionsafaire={}
        self.pulsars=[]
        self.systemes=[]
        self.terrain=[]
        self.creersystemes()
        
    def creersystemes(self):
        
        for i in range(self.nbsystemes):
            x=random.randrange(self.diametre*10)/10
            y=random.randrange(self.diametre*10)/10
            self.systemes.append(Systeme(x,y))
        
        
        for i in range(20):
            x=random.randrange(self.diametre*10)/10
            y=random.randrange(self.diametre*10)/10
            self.pulsars.append(Pulsar(x,y))
            
        np=len(self.joueurscles)
        planes=[]
        systemetemp=self.systemes[:]
        while np:
            p=random.choice(systemetemp)
            if p not in planes and len(p.planetes)>0:
                planes.append(p)
                systemetemp.remove(p)
                np-=1
        couleurs=["cyan","goldenrod","orangered","greenyellow",
                  "dodgerblue","yellow2","maroon1","chartreuse3"]
        
        for i in self.joueurscles:
            self.joueurs[i]=Joueur(self,i,planes.pop(0),couleurs.pop(0))
            
    def creervaisseau(self,systeme):
        self.parent.actions.append([self.parent.monnom,"creervaisseau",systeme])
            
    def prochaineaction(self,cadre):
        if cadre in self.actionsafaire:
            for i in self.actionsafaire[cadre]:
                self.joueurs[i[0]].actions[i[1]](i[2])
            del self.actionsafaire[cadre]
                
        for i in self.joueurscles:
            self.joueurs[i].prochaineaction()
            
        for i in self.pulsars:
            i.evoluer()
            
    def changerproprietaire(self,nom,couleur,syst):
        self.parent.changerproprietaire(nom,couleur,syst)
                
