from collections import defaultdict
import tkinter as tk
import math
import time

fichier = "C:/Users/simon/Desktop/leetcode/projet labyrinthe/cartes/carte.txt"
COULEUR_MUR = "grey"
COULEUR_SOL = "white"
COULEUR_FLECHE = "yellow"
COLONNES_MAX = 200
LIGNES_MAX = 100
VITESSE = 5

class Fenetre:
    def __init__(self, carte, parcours="astar"):
        self.carte = carte
        self.graph = {}
        self.depart = None
        self.arrivee = None
        self.carreaux = []

        self.fenetre = tk.Tk()
        self.width = self.fenetre.winfo_screenwidth()-200
        self.height = self.fenetre.winfo_screenheight()-200
        self.fenetre.geometry(f"{self.width}x{self.height+50}+10+10")

        self.taille_carreau = min(self.width//len(self.carte[0]), self.height//len(self.carte))
        self.canvas = tk.Canvas(self.fenetre, background=COULEUR_SOL)
        self.canvas.pack(expand=True, fill="both")
        self.creer_carte()

        self.frame = tk.Frame(self.fenetre)
        self.frame.pack(side="bottom", fill="both")
        self.choix_parcours = tk.StringVar(value=parcours)
        tk.Radiobutton(self.frame, text="A*",font=("Arial", 16), variable=self.choix_parcours, value="astar", command=self.again).pack(side="left")
        tk.Radiobutton(self.frame, text="Dijkstra",font=("Arial", 16), variable=self.choix_parcours, value="dij", command=self.again).pack(side="left")
        self.label_time = tk.Label(self.frame, text=f"Temps d'exécution : 0", font=("Arial", 14))
        self.label_time.pack(side="left", padx=20)

        tk.Button(self.frame, text="Again", command=self.again, bg="lightblue", width=50).pack(side="right",fill="both", padx=20)

        tk.Button(self.frame, text="Changer la carte", bg="lightblue", width=50, command=self.dessin_carte).pack(side="right", fill="both", padx=20)

        self.fenetre.mainloop()
    
    def creer_carte(self):
        for i in range(len(self.carte)):
            self.carreaux.append([])
            for j in range(len(self.carte[i])):
                haut_gauche = (j*self.taille_carreau, i*self.taille_carreau)
                bas_droite = ((j+1)*self.taille_carreau, (i+1)*self.taille_carreau)
                rempli = COULEUR_SOL if self.carte[i][j] == "-" else COULEUR_MUR
                curr = self.canvas.create_rectangle(haut_gauche, bas_droite, fill=rempli, width=1)
                self.carreaux[i].append(curr)
                self.canvas.tag_bind(curr, "<Button-1>", lambda event, id=curr, row=i, col=j : self.choix_depart_arrivee(event, id, row, col))
    
    def choix_depart_arrivee(self, event, id, row, col):
        if self.canvas.itemcget(id, "fill") == COULEUR_MUR: return
        if self.depart is None:
            self.depart = (row, col)
            self.canvas.itemconfigure(id, fill="green")
        elif self.arrivee is None:
            self.arrivee = (row, col)
            self.canvas.itemconfigure(id, fill="red")
            self.creer_graph()
            debut = time.time()
            chemin, k, to_green, to_blue = self.astar() if self.choix_parcours.get() == "astar" else self.dij()
            self.label_time["text"] = f"Temps d'exécution : {time.time()-debut : .4f} s"
            if chemin is None:
                print("none")
                self.again()
                return
            self.change_mode("disabled")
            for task in to_green:
                self.canvas.after(task[1], self.changer_couleur, task[0], "lightgreen")
            for task in to_blue:
                self.canvas.after(task[1], self.changer_couleur, task[0], "lightblue")
            chemin = [(b*self.taille_carreau+self.taille_carreau//2, a*self.taille_carreau+self.taille_carreau//2) for (a,b) in chemin]
            self.canvas.after(k, self.ligne, chemin)
            self.canvas.after(k+VITESSE*len(chemin), self.change_mode, "normal")
            
    def dij(self):
        def pop_min(dict):
            res = 0
            mini = math.inf
            for node,dist in dict.items():
                if dist < mini:
                    res = node
                    mini = dist
            return res, dict.pop(res)

        k = 0
        to_green = []
        to_blue = []
        a_explorer = {self.depart:0}
        chemins = {self.depart: [self.depart]}
        deja_collectes = {}
        while len(a_explorer) != 0:
            curr, dist = pop_min(a_explorer)
            deja_collectes[curr] = dist
            if curr != self.depart:
                to_blue.append((self.carreaux[curr[0]][curr[1]], k))
                k += VITESSE
            for voi in self.graph[curr]:
                long = Fenetre.distance(voi, curr)
                nouv_dist = dist + long
                if voi not in deja_collectes and nouv_dist < a_explorer.get(voi, math.inf):
                    a_explorer[voi] = nouv_dist
                    chemins[voi] = chemins[curr]+[voi]
                    if voi == self.arrivee: return chemins[voi], k, to_green, to_blue
                    to_green.append((self.carreaux[voi[0]][voi[1]], k))
                    k += VITESSE
        return None, 0, [], []
    
    def astar(self):
        def find_min(dic):
            som_min, mini = (0,0), math.inf
            for som, tup in dic.items():
                if tup[0]+tup[1] < mini:
                    mini = tup[0]+tup[1]
                    som_min = som
            return som_min    
        open_list = {self.depart: [0, 0, None]} # sommet : [distance depart, distance arrivee, parent]
        closed_list = {}
        k = 0
        to_green = []
        to_blue = []
        while len(open_list) > 0:
            curr = find_min(open_list)
            if curr != self.depart:
                to_blue.append((self.carreaux[curr[0]][curr[1]], k))
                k += VITESSE
            for voisin in self.graph[curr]:
                new_w = open_list[curr][0] + Fenetre.distance(curr, voisin)
                distance = Fenetre.distance(voisin, self.arrivee)
                if voisin in closed_list: continue
                if voisin == self.arrivee:
                    open_list[voisin] = [new_w, distance, curr]
                    closed_list[voisin] = open_list[voisin][2]
                    closed_list[curr] = open_list[curr][2]
                    chemin = [self.arrivee]
                    while chemin[0] != self.depart:
                        chemin.insert(0, closed_list[chemin[0]])
                    return chemin, k, to_green, to_blue
                if not voisin in open_list or new_w + distance < open_list[voisin][0]+open_list[voisin][1]:
                    open_list[voisin] = [new_w, distance, curr]
                    to_green.append((self.carreaux[voisin[0]][voisin[1]], k))
                    k += VITESSE
                
            closed_list[curr] = open_list[curr][2]
            open_list.pop(curr)
        return None, 0, [], []

    def changer_couleur(self, id, couleur):
        self.canvas.itemconfigure(id, fill=couleur)
    
    def ligne(self, chemin):
        if len(chemin) >= 2:
            self.canvas.create_line(chemin[:2], fill=COULEUR_FLECHE, width=2)
            self.canvas.after(VITESSE, self.ligne, chemin[1:])
    
    # def jump_point_search(self):
    #     def jump(suiv,node):
    #         dir = (dans_inter(suiv[0]-node[0], -1,1),dans_inter(suiv[1]-node[1], -1,1))
    #         if hors_map(suiv): # hors map
    #             return
    #         if self.carte[suiv[0]][suiv[1]] == "#": # obstacle
    #             return
    #         if suiv == self.arrivee: return suiv

    #         if neighbours(suiv, curr)[1]: # a un forcé
    #             return suiv

    #         if dir[0] != 0 and dir[1] != 0: # mouv diago
    #             if jump((suiv[0],suiv[1]+1), suiv):
    #                 return suiv
    #             if jump((suiv[0]+1,node[1]), suiv):
    #                 return suiv

    #         return jump((suiv[0]+dir[0], suiv[1]+dir[1]), suiv)

    #     def neighbours(node, parent):
    #         if parent is None: # depart dir = (0,0)
    #             i = node[0]
    #             j = node[1]
    #             res = [[],False]
    #             if i > 0 and j > 0 and self.carte[i-1][j-1] == "-" and (self.carte[i-1][j] == "-" or self.carte[i][j-1] == "-"): res[0].append((i-1, j-1))
    #             if i > 0 and self.carte[i-1][j] == "-": res[0].append((i-1, j))
    #             if i > 0 and j < len(self.carte[i])-1 and self.carte[i-1][j+1] == "-" and (self.carte[i-1][j] == "-" or self.carte[i][j+1] == "-"): res[0].append((i-1, j+1))

    #             if j > 0 and self.carte[i][j-1] == "-": res[0].append((i, j-1))
    #             if j < len(self.carte[i])-1 and self.carte[i][j+1] == "-": res[0].append((i, j+1))

    #             if i < len(self.carte)-1 and j > 0 and self.carte[i+1][j-1] == "-" and (self.carte[i+1][j] == "-" or self.carte[i][j-1] == "-"): res[0].append((i+1, j-1))
    #             if i < len(self.carte)-1 and self.carte[i+1][j] == "-": res[0].append((i+1, j))
    #             if i < len(self.carte)-1 and j < len(self.carte[i])-1 and self.carte[i+1][j+1] == "-" and (self.carte[i+1][j] == "-" or self.carte[i][j+1] == "-"): res[0].append((i+1, j+1))
    #             return res
    #         res = [[], False]
    #         dir = (dans_inter(node[0]-parent[0], -1,1),dans_inter(node[1]-parent[1], -1,1))
    #         suiv = (node[0]+dir[0],node[1]+dir[1])

    #         if dir[0] == 0 or dir[1] == 0: # cardinal move
    #             # voisins naturels
    #             if not hors_map(suiv) and not self.carte[suiv[0]][suiv[1]] == "#": res[0].append(suiv)

    #             # voisins forcés
    #             for k in [-1,1]:
    #                 dir_f = (k*dir[1],k*dir[0])
    #                 suiv_f = (node[0]+dir_f[0],node[1]+dir_f[1])
    #                 if not hors_map(suiv_f) and self.carte[suiv_f[0]][suiv_f[1]] == "#":
    #                     forced = (suiv_f[0]+dir[0],suiv_f[1]+dir[1])
    #                     if not hors_map(forced) and not self.carte[forced[0]][forced[1]] == "#":
    #                         res[0].append(forced)
    #                         res[1] = True
    #             return res
    #         # diagonale
    #         # voisins naturels
    #         if not hors_map(suiv) and not self.carte[suiv[0]][suiv[1]] == "#" and (self.carte[suiv[0]][node[1]] == "-" or self.carte[node[0]][suiv[1]] == "-"): res[0].append(suiv)
    #         suiv = (node[0],node[1]+dir[1])
    #         if not hors_map(suiv) and not self.carte[suiv[0]][suiv[1]] == "#": res[0].append(suiv)
    #         suiv = (node[0]+dir[0],node[1])
    #         if not hors_map(suiv) and not self.carte[suiv[0]][suiv[1]] == "#": res[0].append(suiv)

    #         # voisins forcés
    #         prec = (node[0]-dir[0],node[1]-dir[1])
    #         for k in range(2):
    #             dir_f = (k*dir[0],((k+1)%2)*dir[1])
    #             suiv_f = (prec[0]+dir_f[0],prec[1]+dir_f[1])
    #             if not hors_map(suiv_f) and self.carte[suiv_f[0]][suiv_f[1]] == "#":
    #                 forced = (suiv_f[0]+dir_f[0],suiv_f[1]+dir_f[1])
    #                 if not hors_map(forced) and not self.carte[forced[0]][forced[1]] == "#":
    #                     res[0].append(forced)
    #                     res[1] = True
    #         return res

    #     def dans_inter(val, min, max):
    #         return sorted([min, val, max])[1]
    #     def hors_map(node):
    #         if node[0]<0 or node[1]<0 or node[0]>=len(self.carte) or node[1]>=len(self.carte[0]):
    #             return True
    #         return False

    #     open_list = {self.depart: [0, 0, None]} # sommet : [distance depart, distance arrivee, parent]
    #     closed_list = {}
    #     while open_list:
    #         curr = Fenetre.find_min(open_list)
    #         if curr != self.depart:
    #             self.canvas.itemconfigure(self.carreaux[curr[0]][curr[1]], fill="blue")

    #         voisins = neighbours(curr, open_list[curr][2])
    #         for voisin in voisins[0]:
    #             n = jump(voisin, curr)
    #             if not n: continue
    #             new_w = open_list[curr][0] + Fenetre.distance(curr, n)
    #             distance = Fenetre.distance(n, self.arrivee)

    #             if n in closed_list: continue
    #             if not n in open_list or new_w + distance < open_list[n][0]+open_list[n][1]:
    #                 open_list[n] = [new_w, distance, curr]
    #             if n == self.arrivee:
    #                 closed_list[n] = open_list[n][2]
    #                 closed_list[curr] = open_list[curr][2]
    #                 chemin = [self.arrivee]
    #                 while chemin[0] != self.depart:
    #                     chemin.insert(0, closed_list[chemin[0]])
    #                 return chemin
    #             self.canvas.itemconfigure(self.carreaux[n[0]][n[1]], fill="lightgreen")

    #         closed_list[curr] = open_list[curr][2]
    #         open_list.pop(curr)

        
    def again(self):
        self.fenetre.destroy()
        Fenetre(self.carte, self.choix_parcours.get())
    
    def change_mode(self, mode):
        for widget in self.frame.winfo_children():
            widget["state"] = mode
    
    def dessin_carte(self):
        self.fenetre.destroy()
        DessinCarte(self.carte)
    
    def creer_graph(self):
        self.graph = defaultdict(list)
        for i in range(len(self.carte)):
            for j in range(len(self.carte[i])):
                if self.carte[i][j] == "-":
                    if i > 0 and j > 0 and self.carte[i-1][j-1] == "-" and (self.carte[i-1][j] == "-" or self.carte[i][j-1] == "-"): self.graph[(i,j)].append((i-1, j-1))
                    if i > 0 and self.carte[i-1][j] == "-": self.graph[(i,j)].append((i-1, j))
                    if i > 0 and j < len(self.carte[i])-1 and self.carte[i-1][j+1] == "-" and (self.carte[i-1][j] == "-" or self.carte[i][j+1] == "-"): self.graph[(i,j)].append((i-1, j+1))

                    if j > 0 and self.carte[i][j-1] == "-": self.graph[(i,j)].append((i, j-1))
                    if j < len(self.carte[i])-1 and self.carte[i][j+1] == "-": self.graph[(i,j)].append((i, j+1))

                    if i < len(self.carte)-1 and j > 0 and self.carte[i+1][j-1] == "-" and (self.carte[i+1][j] == "-" or self.carte[i][j-1] == "-"): self.graph[(i,j)].append((i+1, j-1))
                    if i < len(self.carte)-1 and self.carte[i+1][j] == "-": self.graph[(i,j)].append((i+1, j))
                    if i < len(self.carte)-1 and j < len(self.carte[i])-1 and self.carte[i+1][j+1] == "-" and (self.carte[i+1][j] == "-" or self.carte[i][j+1] == "-"): self.graph[(i,j)].append((i+1, j+1))
    
    @staticmethod
    def distance(depart, arrivee):
        # return abs(depart[0]-arrivee[0])+abs(depart[1]-arrivee[1])
        # return math.sqrt((depart[0]-arrivee[0])**2+(depart[1]-arrivee[1])**2)
        # return (depart[0]-arrivee[0])**2+(depart[1]-arrivee[1])**2
        dx, dy = abs(depart[0]-arrivee[0]), abs(depart[1]-arrivee[1])
        return 1.414*min(dx, dy)+abs(dx-dy)
        
    

class DessinCarte:
    def __init__(self, carte):
        self.carreaux = []
        self.carte = carte

        self.fenetre = tk.Tk()
        self.width = self.fenetre.winfo_screenwidth()-200
        self.height = self.fenetre.winfo_screenheight()-200
        self.fenetre.geometry(f"{self.width}x{self.height+50}+10+10")

        self.taille_carreau = min(self.width//len(self.carte[0]), self.height//len(self.carte))
        self.canvas = tk.Canvas(self.fenetre, background=COULEUR_SOL)
        self.canvas.pack(expand=True, fill="both")
        self.creer_carte()
        self.canvas.bind("<B1-Motion>", self.ajouter_mur)
        self.canvas.bind("<B3-Motion>", self.enlever_mur)
        self.canvas.bind("<Button-1>", self.ajouter_mur)
        self.canvas.bind("<Button-3>", self.enlever_mur)

        self.nombre_lignes = tk.StringVar(self.fenetre, str(len(self.carte)))
        self.nombre_colonnes = tk.StringVar(self.fenetre, str(len(self.carte[0])))
        frame = tk.Frame(self.fenetre)
        frame.pack(side="bottom", fill="both")

        tk.Label(frame, text=f"Nombre de lignes :").pack(side="left", padx=20)
        tk.Scale(frame, variable=self.nombre_lignes, from_=2, to=LIGNES_MAX, command=self.changer_lignes, orient="horizontal").pack(side="left")
        tempspin = tk.Spinbox(frame, textvariable=self.nombre_lignes, from_=2, to=LIGNES_MAX, command=lambda : self.changer_lignes(self.nombre_lignes.get()))
        tempspin.bind("<Return>", lambda event : self.changer_lignes(self.nombre_lignes.get()))
        tempspin.pack(side="left")

        tk.Label(frame, text=f"Nombre de colonnes :").pack(side="left", padx=20)
        tk.Scale(frame, variable=self.nombre_colonnes, from_=2, to=COLONNES_MAX, command=self.changer_colonnes, orient="horizontal").pack(side="left")
        tempspin = tk.Spinbox(frame, textvariable=self.nombre_colonnes, from_=2, to=COLONNES_MAX, command=lambda : self.changer_colonnes(self.nombre_colonnes.get()))
        tempspin.bind("<Return>", lambda event : self.changer_colonnes(self.nombre_colonnes.get()))
        tempspin.pack(side="left")

        tk.Button(frame, text="Confirmer", bg="lightblue", width=50, height=2, command=self.confirmer).pack(side="right", fill="both", padx=20)
        tk.Button(frame, text="Effacer", bg="lightblue", width=50, height=2, command=self.effacer_carte).pack(side="right", fill="both", padx=20)

        self.fenetre.mainloop()
    
    def creer_carte(self):
        self.taille_carreau = min(self.width//len(self.carte[0]), self.height//len(self.carte))
        self.carreaux = []
        self.canvas.delete("all")
        for i in range(len(self.carte)):
            self.carreaux.append([])
            for j in range(len(self.carte[i])):
                haut_gauche = (j*self.taille_carreau, i*self.taille_carreau)
                bas_droite = ((j+1)*self.taille_carreau, (i+1)*self.taille_carreau)
                rempli = COULEUR_SOL if self.carte[i][j] == "-" else COULEUR_MUR
                curr = self.canvas.create_rectangle(haut_gauche, bas_droite, fill=rempli, width=1)
                self.carreaux[i].append(curr)
    
    def changer_lignes(self, val):
        while len(self.carte) > int(val):
            self.carte.pop(-1)
        while len(self.carte) < int(val):
            self.carte.append("-"*len(self.carte[0]))
        self.creer_carte()
    
    def changer_colonnes(self, val):
        while len(self.carte[0]) > int(val):
            self.carte = [ligne[:-1] for ligne in self.carte]
        while len(self.carte[0]) < int(val):
            self.carte = [ligne+"-" for ligne in self.carte]
        self.creer_carte()
    
    def ajouter_mur(self, event):
        id = self.canvas.find_closest(event.x, event.y, halo=None, start=None)
        row = (event.y // self.taille_carreau)%len(self.carte)
        col = (event.x // self.taille_carreau)%len(self.carte[0])
        if self.canvas.itemcget(id, "fill") == COULEUR_SOL:
            self.canvas.itemconfigure(id, fill=COULEUR_MUR)
            self.carte[row] = self.carte[row][:col]+"#"+self.carte[row][col+1:]

    def enlever_mur(self, event):
        id = self.canvas.find_closest(event.x, event.y, halo=None, start=None)
        row = event.y // self.taille_carreau
        col = event.x // self.taille_carreau
        if self.canvas.itemcget(id, "fill") == COULEUR_MUR:
            self.canvas.itemconfigure(id, fill=COULEUR_SOL)
            self.carte[row] = self.carte[row][:col]+"-"+self.carte[row][col+1:]
    
    def effacer_carte(self):
        self.carte = ["-"*len(row) for row in self.carte]
        self.creer_carte()
    
    def confirmer(self):
        with open(fichier, "w") as f:
            for row in self.carte:
                f.write(row)
                f.write("\n")
        self.fenetre.destroy()
        Fenetre(self.carte)

with open(fichier, "r") as f:
    carte = [line.strip() for line in f.readlines()]
Fenetre(carte)