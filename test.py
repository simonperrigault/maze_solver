carte = [
    "---",
    "--#",
    "-#-"
]

def neighbours(node, parent):
    res = [[], False]
    dir = (dans_inter(node[0]-parent[0], -1,1),dans_inter(node[1]-parent[1], -1,1))
    suiv = (node[0]+dir[0],node[1]+dir[1])

    if dir[0] == 0 or dir[1] == 0: # cardinal move
        # voisins naturels
        if not hors_map(suiv) and not carte[suiv[0]][suiv[1]] == "#": res[0].append(suiv)

        # voisins forcés
        for k in [-1,1]:
            dir_f = (k*dir[1],k*dir[0])
            suiv_f = (node[0]+dir_f[0],node[1]+dir_f[1])
            if not hors_map(suiv_f) and carte[suiv_f[0]][suiv_f[1]] == "#":
                forced = (suiv_f[0]+dir[0],suiv_f[1]+dir[1])
                if not hors_map(forced) and not carte[forced[0]][forced[1]] == "#":
                    res[0].append(forced)
                    res[1] = True
        return res
    # diagonale
    # voisins naturels
    if not hors_map(suiv) and not carte[suiv[0]][suiv[1]] == "#" and (carte[suiv[0]][node[1]] == "-" or carte[node[0]][suiv[1]] == "-"): res[0].append(suiv)
    suiv = (node[0],node[1]+dir[1])
    if not hors_map(suiv) and not carte[suiv[0]][suiv[1]] == "#": res[0].append(suiv)
    suiv = (node[0]+dir[0],node[1])
    if not hors_map(suiv) and not carte[suiv[0]][suiv[1]] == "#": res[0].append(suiv)

    # voisins forcés
    prec = (node[0]-dir[0],node[1]-dir[1])
    for k in range(2):
        dir_f = (k*dir[0],((k+1)%2)*dir[1])
        suiv_f = (prec[0]+dir_f[0],prec[1]+dir_f[1])
        if not hors_map(suiv_f) and carte[suiv_f[0]][suiv_f[1]] == "#":
            forced = (suiv_f[0]+dir_f[0],suiv_f[1]+dir_f[1])
            if not hors_map(forced) and not carte[forced[0]][forced[1]] == "#":
                res[0].append(forced)
                res[1] = True
    return res
def dans_inter(val, min, max):
    return sorted([min, val, max])[1]
def hors_map(node):
    if node[0]<0 or node[1]<0 or node[0]>=len(carte) or node[1]>=len(carte[0]):
        return True
    return False
print(neighbours((1,1), (-1,-1)))