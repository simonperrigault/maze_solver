from collections import defaultdict
import tkinter as tk
import math
import time

fichier = "cartes/carte.txt"
COULEUR_MUR = "grey"
COULEUR_SOL = "white"
COULEUR_FLECHE = "black"
COLONNES_MAX = 200
LIGNES_MAX = 100
PERIODE_ANIM = 2
TAILLE_FLECHE = 5

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
        tk.Radiobutton(self.frame, text="JPS",font=("Arial", 16), variable=self.choix_parcours, value="jps", command=self.again).pack(side="left")
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
            if self.choix_parcours.get() == "jps":
                chemin, k, to_green, to_blue = self.jump_point()
            elif self.choix_parcours.get() == "dij":
                chemin, k, to_green, to_blue = self.dij()
            else:
                chemin, k, to_green, to_blue = self.astar()
            self.label_time["text"] = f"Temps d'exécution : {time.time()-debut : .4f} s"
            if chemin is None:
                print("Aucun chemin trouvé")
                self.again()
                return
            self.change_mode("disabled")
            for task in to_green:
                self.canvas.after(task[1], self.changer_couleur, task[0], "lightgreen")
            for task in to_blue:
                self.canvas.after(task[1], self.changer_couleur, task[0], "lightblue")
            chemin = [(b*self.taille_carreau+self.taille_carreau//2, a*self.taille_carreau+self.taille_carreau//2) for (a,b) in chemin]
            self.canvas.after(k, self.ligne, chemin)
            self.canvas.after(k+PERIODE_ANIM*len(chemin), self.change_mode, "normal")
            
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
                k += PERIODE_ANIM
            for voi in self.graph[curr]:
                long = Fenetre.distance(voi, curr)
                nouv_dist = dist + long
                if voi not in deja_collectes and nouv_dist < a_explorer.get(voi, math.inf):
                    a_explorer[voi] = nouv_dist
                    chemins[voi] = chemins[curr]+[voi]
                    if voi == self.arrivee: return chemins[voi], k, to_green, to_blue
                    to_green.append((self.carreaux[voi[0]][voi[1]], k))
                    k += PERIODE_ANIM
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
                k += PERIODE_ANIM
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
                    k += PERIODE_ANIM
                
            closed_list[curr] = open_list[curr][2]
            open_list.pop(curr)
        return None, 0, [], []
    
    def jump_point(self):
        open_list = {self.depart: (0, 0, None)} # sommet : [distance depart, distance arrivee, parent]
        closed_list = {}
        to_green = []
        to_blue = []
        k = 0
        
        def find_min(dic):
            som_min, mini = (0,0), math.inf
            for som, tup in dic.items():
                if tup[0]+tup[1] < mini:
                    mini = tup[0]+tup[1]
                    som_min = som
            return som_min
        
        def natural_neigh(curr, dx, dy):
            parent = (curr[0] - dx, curr[1] - dy)
            res = []
            if dx*dy == 0: # cardinal
                if self.verif_coor(curr[0]+dx, curr[1]+dy) and self.carte[curr[0]+dx][curr[1]+dy] == "-":
                    res.append((curr[0]+dx, curr[1]+dy))
            else:
                if self.verif_coor(curr[0]+dx, curr[1]+dy) and self.carte[curr[0]+dx][curr[1]+dy] == "-":
                    res.append((curr[0]+dx, curr[1]+dy))
                if self.verif_coor(curr[0], curr[1]+dy) and self.carte[curr[0]][curr[1]+dy] == "-":
                    res.append((curr[0], curr[1]+dy))
                if self.verif_coor(curr[0]+dx, curr[1]) and self.carte[curr[0]+dx][curr[1]] == "-":
                    res.append((curr[0]+dx, curr[1]))
            return res
        
        def forced_neigh(curr, dx, dy):
            parent = (curr[0] - dx, curr[1] - dy)
            res = []
            if dx*dy == 0:
                if self.verif_coor(curr[0]-dy, curr[1]+dx) and self.carte[curr[0]-dy][curr[1]+dx] == "#" and self.verif_coor(curr[0]-dy+dx, curr[1]+dx+dy) and self.carte[curr[0]-dy+dx][curr[1]+dx+dy] == "-":
                    res.append((curr[0]-dy+dx, curr[1]+dx+dy))
                if self.verif_coor(curr[0]+dy, curr[1]-dx) and self.carte[curr[0]+dy][curr[1]-dx] == "#" and self.verif_coor(curr[0]+dy+dx, curr[1]-dx+dy) and self.carte[curr[0]+dy+dx][curr[1]-dx+dy] == "-":
                    res.append((curr[0]+dy+dx, curr[1]-dx+dy))
            else:
                if self.verif_coor(parent[0]+dx, parent[1]) and self.carte[parent[0]+dx][parent[1]] == "#" and self.verif_coor(parent[0]+2*dx, parent[1]) and self.carte[parent[0]+2*dx][parent[1]] == "-":
                    res.append((parent[0]+2*dx, parent[1]))
                if self.verif_coor(parent[0], parent[1]+dy) and self.carte[parent[0]][parent[1]+dy] == "#" and self.verif_coor(parent[0], parent[1]+2*dy) and self.carte[parent[0]][parent[1]+2*dy] == "-":
                    res.append((parent[0], parent[1]+2*dy))
            return res
        
        def jump(curr, dx, dy):
            n = (curr[0]+dx, curr[1]+dy)
            if n[0] < 0 or n[1] < 0 or n[0] > len(self.carte)-1 or n[1] > len(self.carte[0])-1 or self.carte[n[0]][n[1]] == "#":
                return None
            if self.verif_coor(curr[0]-dx, curr[1]-dy) and self.carte[curr[0]-dx][curr[1]] == "#" and self.carte[curr[0]][curr[1]-dy] == "#":
                return None
            if n == self.arrivee:
                return n
            if len(forced_neigh(n, dx, dy)) != 0:
                return n
            if dx*dy != 0:
                if jump(n, dx, 0) is not None:
                    return n
                if jump(n, 0, dy) is not None:
                    return n
            return jump(n, dx, dy)
        
        def add_successors(curr, parent):
            nonlocal k
            if parent is None:
                for n in self.graph[curr]:
                    open_list[n] = (Fenetre.distance(curr, n), Fenetre.distance(n, self.arrivee), curr)
                    to_green.append((self.carreaux[n[0]][n[1]], k))
                    k += PERIODE_ANIM
            else:
                dx = curr[0] - parent[0]
                dx = 0 if dx == 0 else dx//abs(dx)
                dy = curr[1] - parent[1]
                dy = 0 if dy == 0 else dy//abs(dy)
                neigh = natural_neigh(curr, dx, dy) + forced_neigh(curr, dx, dy)
                for n in neigh:
                    n = jump(curr, n[0]-curr[0], n[1]-curr[1])
                    if n is not None:
                        open_list[n] = (open_list[curr][0] + Fenetre.distance(curr, n), Fenetre.distance(n, self.arrivee), curr)
                        if n == self.arrivee: continue
                        to_green.append((self.carreaux[n[0]][n[1]], k))
                        k += PERIODE_ANIM
        
        while len(open_list) > 0:
            curr = find_min(open_list)
            if curr == self.arrivee:
                closed_list[curr] = open_list[curr][2]
                chemin = [self.arrivee]
                while chemin[0] != self.depart:
                    chemin.insert(0, closed_list[chemin[0]])
                return chemin, k, to_green, to_blue
            if curr != self.depart:
                to_blue.append((self.carreaux[curr[0]][curr[1]], k))
                k += PERIODE_ANIM
            add_successors(curr, open_list[curr][2])
            closed_list[curr] = open_list[curr][2]
            open_list.pop(curr)
        return None, 0, [], []
        

    def changer_couleur(self, id, couleur):
        self.canvas.itemconfigure(id, fill=couleur)
    
    def ligne(self, chemin):
        if len(chemin) >= 2:
            self.canvas.create_line(chemin[:2], fill=COULEUR_FLECHE, width=TAILLE_FLECHE)
            self.canvas.after(PERIODE_ANIM, self.ligne, chemin[1:])
    
    
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
    
    def verif_coor(self, x, y):
        return 0 <= x < len(self.carte) and 0 <= y < len(self.carte[0])
    
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