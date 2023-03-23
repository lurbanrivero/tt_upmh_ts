#!/usr/bin/python3

from pulp import *
import sys


class profesor:
    def __init__(self, clave, nombre, contrato, hrs_min, hrs_max, disp, pref):
        self.nombre = nombre
        self.clave = clave
        self.contrato = contrato
        self.hrs_min = hrs_min
        self.hrs_max = hrs_max
        self.pref = pref.split(" ")
        self.dias_idx = {}
        self.dias_c = {}
        self.dias_matr = {}
        for i in range(0, 5):
            if (disp[i] != '') and (disp[i] != '-') and (disp[i] != '-\n'):
                dia_cn = []
                dia_c = []
                dia_s = disp[i].split(" ")
                # print(dia_s)
                for dia in dia_s:
                    disp_c = dia.split("-")
                    lb = int(disp_c[0])
                    ub = int(disp_c[1])
                    t = lb
                    while t < ub:
                        dia_cn.append(t-7)
                        dia_c.append(str(t)+"-"+str(t+1))
                        t = t+1
                self.dias_idx[i] = dia_cn
                self.dias_c[i] = dia_c
            else:
                self.dias_idx[i] = []
                self.dias_c[i] = []
        for d in range(0, 5):
            for t in range(0, 14):
                self.dias_matr[d, t] = 0

        for d in range(0, 5):
            for t in range(0, len(self.dias_idx[d])):
                self.dias_matr[d, self.dias_idx[d][t]] = 1
            # print(dias)


class curso:
    def __init__(self, clave, gr, nombre, hrs, fijo, mins, maxs, preferencias, horario={}):
        self.clave = clave
        self.gr = gr
        self.nombre = nombre
        self.hrs = hrs
        self.dias = {}
        self.fijo = fijo
        self.mins = mins
        self.maxs = maxs
        self.preferencias = preferencias
        if self.fijo == 1:
            for d in range(0, 5):
                for t in range(0, 14):
                    self.dias[d, t] = 0
            for d in range(0, 5):
                if (horario[d] != '') and (horario[d] != '-') and (horario[d] != '-\n'):
                    # print(horario[d])
                    dia = horario[d].split("-")
                    lb = int(dia[0])
                    ub = int(dia[1])
                    for t in range(0, 14):
                        if (t+7) >= lb and (t+7) < ub:
                            self.dias[d, t] = 1


class grupo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.cursos = []

    def add_curso(self, curso):
        self.cursos.append(curso)


def busca_grupo(grupos, gr):
    for i in range(0, len(grupos)):
        if gr.nombre == grupos[i].nombre:
            return i
            break
    return -1


def idx_curso(cursos, p):
    indices = []
    for i in range(0, len(cursos)):
        if cursos[i].clave == p:
            indices.append(i)
    return indices


def idx_curso_grupo(cursos, g):
    indices = []
    for i in range(0, len(cursos)):
        for k in range(0, len(grupos[g].cursos)):
            if cursos[i].clave == grupos[g].cursos[k].clave and cursos[i].gr == grupos[g].cursos[k].nombre:
                indices.append(i)
    return indices


def fijos_no_fijos(cursos, grupos, g):
    fijos = []
    nofijos = []
    for j in grupos[g].cursos:
        if cursos[j].fijo == 1:
            fijos.append(j)
        else:
            nofijos.append(j)
    return [fijos, nofijos]


def f_preferencias(profesores, cursos, y):
    s = 0
    for i in range(0, len(profesores)):
        for j in range(0, len(cursos)):
            s = s+(10000*y[i, j])

    for i in range(0, len(profesores)):
        for k in range(0, len(profesores[i].pref)):
            indices = idx_curso(cursos, profesores[i].pref[k])
            # print(indices)
            if len(indices) > 0:
                for q in indices:
                    s = s + ((k-10000) * y[i, q])

    return s


def suma_fuera_de_horario(cursos, x, D, T, N):
    s = 0
    for j in range(0, len(cursos)):
        if int(cursos[j].gr[0]) <= 4:
            for i in range(0, N):
                for t in range(0, T):
                    if t >= 8:
                        for d in range(0, D):
                            s = s+1000*x[i, j, t, d]
        elif int(cursos[j].gr[0]) > 4:
            for i in range(0, N):
                for t in range(0, T):
                    if t >= 0 and t < 8:
                        for d in range(0, D):
                            s = s+1000*x[i, j, t, d]
    return s


def imprime_profesor(nombre, p, profesores, cursos, x, T, D):
    fh_horario_profesor = open(nombre+"_profr_"+str(p)+".csv", "w")
    fh_horario_profesor.write("Horario del profesor \n"+profesores[p].nombre+"\n \n")
    fh_horario_profesor.write("Hora/Dia,Lunes,Martes,Miercoles,Jueves,Viernes\n")
    for t in range(0, T):
        fh_horario_profesor.write(str(t+7)+"-"+str(t+8)+",")
        for d in range(0, D):
            for j in range(0, len(cursos)):
                if abs(x[p, j, t, d].varValue) > 0.0001:
                    fh_horario_profesor.write(cursos[j].clave+" "+cursos[j].gr)
            fh_horario_profesor.write(",")
        fh_horario_profesor.write("\n")

    fh_horario_profesor.write("\n")

    fh_horario_profesor.write("Hora/Dia,Lunes,Martes,Miercoles,Jueves,Viernes\n")
    total=0.0
    colocados=0.0
    for t in range(0, T):
        fh_horario_profesor.write(str(t+7)+"-"+str(t+8)+",")
        for d in range(0, D):
            for j in range(0, len(cursos)):
                if abs(x[p, j, t, d].varValue) > 0.0001:
                    fh_horario_profesor.write(str(profesores[i].dias_matr[d, t]))
                    colocados+=profesores[i].dias_matr[d,t]
                    total+=1
            fh_horario_profesor.write(",")
        fh_horario_profesor.write("\n")
    c_pref=0
    c_asig=0
    for j in range(0,len(cursos)):
        if abs(y[i,j].varValue) > 0.0001:
            bandera=0
            for k in range(0, len(profesores[i].pref)):
            #indices = idx_curso(cursos, profesores[i].pref[k])
                if cursos[j].clave==profesores[i].pref[k]:
                    fh_horario_profesor.write(profesores[i].pref[k]+":"+str(k)+",")
                    bandera=1
                    c_pref+=1
                    break
            if bandera==0:    
                fh_horario_profesor.write(cursos[j].clave+":"+str(1000)+",")
            c_asig+=1    
    fh_horario_profesor.close()        
    if total > 0.0 and c_asig > 0.0:    
        return [colocados/total,c_pref/c_asig]
    elif total > 0.0 and c_asig == 0.0:
        return [colocados/total,-1]
    elif total == 0.0 and c_asig > 0.0:
        return [-1,c_pref/c_asig]        
    else:
        return [-1.0,-1.0]         


def imprime_grupo(nombre, g, grupos, cursos, x, N, T, D):
    fh_horario_grupo = open(nombre+"_grupo_"+str(g)+".csv", "w")
    fh_horario_grupo.write("Horario del grupo "+grupos[g].nombre+"\n \n")
    fh_horario_grupo.write("Hora/Dia,Lunes,Martes,Miercoles,Jueves,Viernes\n")
    for t in range(0, T):
        fh_horario_grupo.write(str(t+7)+"-"+str(t+8)+",")
        for d in range(0, D):
            for j in grupos[g].cursos:
                for i in range(0, N):
                    if abs(x[i, j, t, d].varValue) > 0.0001:
                        fh_horario_grupo.write(cursos[j].clave)
            fh_horario_grupo.write(",")
        fh_horario_grupo.write("\n")
    fh_horario_grupo.close()


class turno:
    def __init__(self, grupos, horario):
        self.grupos = grupos
        hrs = horario.split("-")
        lb = int(hrs[0])
        ub = int(hrs[1])
        self.horas = []
        self.horas_comp = []
        for t in range(0, 14):
            if (t+7) >= lb and (t+7) < ub:
                self.horas.append(t)
            else:
                self.horas_comp.append(t)


def busca_turno(lista, tr):
    for k in range(0, len(lista)):
        if lista[k] == tr:
            return 1
            break
    return 0


def get_prefijo(palabra, size):
    return (palabra[0:size])


fh_materia = open(sys.argv[1], "r")
fh_profesor = open(sys.argv[2], "r")
fh_fijas = open(sys.argv[3], "r")
fh_turnos = open(sys.argv[4], "r")
nombre = sys.argv[5]


l = 0
turnos = []
for linea in fh_turnos:
    linea2 = linea.rstrip()
    l_list = linea2.split(",")
    grs = l_list[1].split(" ")
    turn = turno(grs, l_list[2])
    turnos.append(turn)


for tu in turnos:
    print(tu.grupos, tu.horas, tu.horas_comp)


l = 0
g = 0
cursos = []
grupos = {}
cg = []
for linea in fh_materia:
    if l == 0:
        l = l+1
    else:
        l_list = linea.split(",")
        pref = l_list[4]
        if pref == "-":
            preferencias = []
        else:
            preferencias = pref.split(" ")
        # print(preferencias)
        c = curso(l_list[0], l_list[1], l_list[2], int(l_list[3]), 0, int(l_list[5]), int(l_list[6]), preferencias)
        # def __init__(self,clave,gr,nombre,hrs,fijo,mins,maxs,preferencias,horarios={}):
        cursos.append(c)
        gr = grupo(l_list[1])
        indice_g = busca_grupo(grupos, gr)
        if (indice_g == -1):
            grupos[g] = gr
            grupos[g].add_curso(len(cursos)-1)
            g = g+1
        else:
            grupos[indice_g].add_curso(len(cursos)-1)
        l = l+1
fh_materia.close()

l = 0
for linea in fh_fijas:
    if l == 0:
        l = l+1
    else:
        l_list = linea.split(",")
        horario = [l_list[5], l_list[6], l_list[7], l_list[8], l_list[9]]
        pref = l_list[4]
        if pref == "-":
            preferencias = []
        else:
            preferencias = pref.split(" ")
        c = curso(l_list[0], l_list[1], l_list[2], int(
            l_list[3]), 1, 1, 8, preferencias, horario)
        cursos.append(c)
        gr = grupo(l_list[1])
        indice_g = busca_grupo(grupos, gr)
        if (indice_g == -1):
            grupos[g] = gr
            grupos[g].add_curso(len(cursos)-1)
            g = g+1
        else:
            grupos[indice_g].add_curso(len(cursos)-1)
        l = l+1
        # c=curso(l_list[0],l_list[1],l_list[2],int(l_list[3]),1)

fh_fijas.close()
profesores = []
l = 0
for linea in fh_profesor:
    if l == 0:
        l = l+1
    else:
        l_list = linea.split(",")
        disp = [l_list[6], l_list[7], l_list[8], l_list[9], l_list[10]]
        # print(disp)
        p = profesor(l_list[0], l_list[1], l_list[3], int(l_list[4]), int(l_list[5]), disp, l_list[2])
        profesores.append(p)
        l = l+1

N = len(profesores)

G = len(grupos)
T = 14
D = 5
M = len(cursos)


mod = LpProblem(sense=LpMinimize)


x = {}
s = {}
for i in range(0, N):
    for j in range(0, M):
        for t in range(0, T):
            for d in range(0, D):
                x[i, j, t, d] = LpVariable("x"+"_"+str(i)+"_"+str(j)+"_"+str(t)+"_"+str(d), 0, 1, LpInteger)

for j in range(0, M):
    for t in range(0, T):
        for d in range(0, D):
            s[j, t, d] = LpVariable(
                "s"+"_"+str(j)+"_"+str(t)+"_"+str(d), 0, 1, LpInteger)


y = {}
for i in range(0, N):
    for j in range(0, M):
        y[i, j] = LpVariable("y_"+str(i)+"_"+str(j), 0, 1, LpInteger)

z = {}

for j in range(0, M):
    for d in range(0, D):
        z[j, d] = LpVariable("z_"+str(j)+"_"+str(d), 0, 1, LpInteger)

st = {}
fin = {}
xt = {}
# st[g,t,d] = 1 Si el horario de el grupo g inicia en la hora t del dia d; 0 en otro caso.
# fin[g,t,d] = 1 Si el horario de el grupo g finaliza en la hora t del dia d; 0 en otro caso.
# xt[g,t,d] = 1 si la hora g puede ser utilizada en el horario del grupo g en la hora t del dia d; 0 en otro caso

for g in range(0, G):
    for t in range(0, T):
        for d in range(0, D):
            st[g, t, d] = LpVariable("st_"+str(g)+"_"+str(t)+"_"+str(d), 0, 1, LpInteger)
            fin[g, t, d] = LpVariable("fin_"+str(g)+"_"+str(t)+"_"+str(d), 0, 1, LpInteger)
            xt[g, t, d] = LpVariable("xt_"+str(g)+"_"+str(t)+"_"+str(d), 0, 1, LpInteger)


op1 = 1  # int(sys.argv[4])

f1 = lpSum([(1-profesores[i].dias_matr[d, t]) * x[i, j, t, d] for i in range(0, N) for j in range(0, M) for t in range(0, T) for d in range(0, D)])
f2 = f_preferencias(profesores, cursos, y)
f3 = lpSum([x[i, j, t, d] for i in range(0, N) if profesores[i].clave =='-1' for j in range(0, M) for d in range(0, D) for t in range(0, T)])

mod.setObjective(100*f1+f2+1000*f3)


for i in range(0, N):
    mod.addConstraint(lpSum([x[i, j, t, d] for j in range(0, M) for t in range(0, T) for d in range(0, D)]) >= profesores[i].hrs_min, "minimo_numero_de_horas_del_profesor_"+str(i))
    mod.addConstraint(lpSum([x[i, j, t, d] for j in range(0, M) for t in range(0, T) for d in range(0, D)]) <= profesores[i].hrs_max, "maximo_numero_de_horas_del_profesor_"+str(i))
    for t in range(0, T):
        for d in range(0, D):
            mod.addConstraint(lpSum([x[i, j, t, d] for j in range(0, M)]) <= 1, "El_profesor_" + str(i)+"_puede_atender_a_lo_mas_1_curso_en_la_hora_"+str(t)+"_durante_el_dia_"+str(d))
h = 0
for j in range(0, M):
    mod.addConstraint(lpSum([y[i, j] for i in range(0, N)]) == 1, "el_curso_" + str(j) + "_necesita_un_profesor")
    for t in range(0, T):
        for d in range(0, D):
            mod.addConstraint(lpSum([x[i, j, t, d] for i in range(0, N)]) <= 1*z[j, d], "el_curso_"+str(j)+"_"+"en_la_hora_"+str(t)+"_en_el_dia_"+str(d)+"debe_tener_a_lo_mas_un_profesor")
            h = h+1
for i in range(0, N):
    for j in range(0, M):
        mod.addConstraint(lpSum([x[i, j, t, d] for t in range(0, T) for d in range(0, D)]) == cursos[j].hrs*y[i, j], "el_profesor_"+str(i) + "_debe_dar_todo_el_curso_" + str(j))

for j in range(0, M):
    for d in range(0, D):
        mod.addConstraint(lpSum([x[i, j, t, d] for i in range(0, N) for t in range(0, T)]) >= cursos[j].mins * z[j, d], "las_sesiones_del_curso_" + str(j) + "_en_el_dia_"+str(d) + "_deben_durar_al_menos_1hr")
        mod.addConstraint(lpSum([x[i, j, t, d] for i in range(0, N) for t in range(0, T)]) <= cursos[j].maxs * z[j, d], "las_sesiones_del_curso_" + str(j) + "_en_el_dia_"+str(d) + "_deben_durar_a_lo_mas_3hr")

for j in range(0, M):
    for d in range(0, D):
        mod.addConstraint(lpSum([s[j, t, d] for t in range( 0, T)]) <= 1 * z[j, d], "inicia_el_curso_"+str(j)+"_el_dia_"+str(d))

for i in range(0, N):
    for j in range(0, M):
        for t in range(0, T):
            for d in range(0, D):
                if t == 0:
                    mod.addConstraint(s[j, t, d] >= x[i, j, t, d], "red_"+str(i)+"_"+str(j)+"_"+str(t)+"_"+str(d))
                else:
                    mod.addConstraint(s[j, t, d] >= x[i, j, t, d]-x[i, j, t-1, d],"red_"+str(i)+"_"+str(j)+"_"+str(t)+"_"+str(d))

for i in range(0, N):
    for g in range(0, G):
        mod.addConstraint(lpSum([y[i, idx] for idx in grupos[g].cursos]) <= 1, "un_solo_profe"+str(i)+"_"+str(grupos[g].nombre))


for t in range(0, T):
    for d in range(0, D):
        for g in range(0, G):
            mod.addConstraint(lpSum([x[i, idx, t, d] for i in range(0, N) for idx in grupos[g].cursos]) <= 1, "materias_simultaneas_en_la_hora_"+str(t)+"_"+str(d)+"_"+str(grupos[g].nombre))


if op1 == 1:
    for j in range(0, M):
        # if int(cursos[j].gr[0])<=4 or int(cursos[j].gr[0])==7:
        for tr in range(0, len(turnos)):
            if busca_turno(turnos[tr].grupos, cursos[j].gr) == 1:
                for i in range(0, N):
                    for t in turnos[tr].horas_comp:
                        for d in range(0, D):
                            mod.addConstraint(x[i, j, t, d] <= 0)
                    # for t in range(0,T):
                    # for d in range(0,D):
                    # if t>=9:
                    # mod.addConstraint(x[i,j,t,d]<=0)
                        # else:
                        # mod.addConstraint(x[i,j,t,d]>=0)
        # elif busca_turno(vespertino,cursos[j].gr)==1:
# else:
# for i in range(0,N):
# for t in range(0,T):
# for d in range(0,D):
# if t>=0 and t<5:
# mod.addConstraint(x[i,j,t,d]<=0)
# #else:
# #	mod.addConstraint(x[i,j,t,d]>=0)


for g in range(0, G):
    [fijos, nofijos] = fijos_no_fijos(cursos, grupos, g)
    for j1 in fijos:
        for d in range(0, D):
            for t in range(0, T):
                if cursos[j1].dias[d, t] == 1:
                    for j2 in nofijos:
                        for i in range(0, N):
                            if profesores[i].clave != '99':
                                mod.addConstraint(x[i, j2, t, d] <= 0)


for i in range(0, N):
    if profesores[i].clave == '99':
        for j in range(0, M):
            if cursos[j].fijo == 1:
                for t in range(0, T):
                    for d in range(0, D):
                        if cursos[j].dias[d, t] == 0:
                            for j2 in range(0, M):
                                if cursos[j2].fijo == 0:
                                    mod.addConstraint(x[i, j2, t, d] <= 0)


# Los cursos de ingles se imparten en horario fijo por algun profesor de inglés

for j in range(0, M):
    if cursos[j].fijo == 1:
        for t in range(0, T):
            for d in range(0, D):
                if cursos[j].dias[d, t] == 1:
                    # print(j,t,d)
                    mod.addConstraint(lpSum([x[i, j, t, d] for i in range(0, N) if profesores[i].clave == '99']) == 1, "ingles_auto_"+str(j)+"_"+str(t)+"_"+str(d))

for i in range(0, N):
    if profesores[i].clave == '99':
        for t in range(0, T):
            for d in range(0, D):
                if cursos[j].dias[d, t] == 1:
                    mod.addConstraint(
                        lpSum([x[i, j, t, d] for j in range(0, M) if cursos[j].fijo == 1]) <= 1)


# for i in range(0,N):
# if profesores[i].clave=='99':
#		mod+=lpSum([y[i,j] for j in range(0,M) if  cursos[j].fijo==1 ])==1

# for j in range(0,M):
# if  cursos[j].fijo==1:
#		mod += lpSum([y[i,j] for i in range(0,N) if profesores[i].clave=='99'])==1

# Los profesores de base y otros especiales deben de dar al menos un curso de tutoria y no mas de 2

for i in range(0, N):
    if profesores[i].clave != '99' and profesores[i].clave != '-1' and profesores[i].contrato == 'Base':
        mod.addConstraint(lpSum([y[i, j] for j in range(0, M) if cursos[j].fijo == 0 and get_prefijo(cursos[j].clave, 4) == 'TGTI']) >= 1, "min_tutoria_individual_para_el_profe_"+str(i))
        mod.addConstraint(lpSum([y[i, j] for j in range(0, M) if cursos[j].fijo == 0 and get_prefijo(cursos[j].clave, 4) == 'TGTI']) <= 2, "max_tutoria_individual_para_el_profe_"+str(i))
        mod.addConstraint(lpSum([y[i, j] for j in range(0, M) if cursos[j].fijo == 0 and get_prefijo(cursos[j].clave, 4) == 'TGTI']) >= 1, "min_tutoria_grupal_para_el_profe_"+str(i))
        mod.addConstraint(lpSum([y[i, j] for j in range(0, M) if cursos[j].fijo == 0 and get_prefijo(cursos[j].clave, 4) == 'TGTI']) <= 2, "max_tutoria_grupal_para_el_profe_"+str(i))
    elif profesores[i].clave == '99':
        mod.addConstraint(lpSum([y[i, j] for j in range(0, M) if cursos[j].fijo == 0 and get_prefijo(cursos[j].clave, 4) == 'TGTI']) <= 0, "max_tutoria_individual_para_el_profe_"+str(i))
    elif profesores[i].clave == '-1':
        mod.addConstraint(lpSum([y[i, j] for j in range(0, M) if cursos[j].fijo == 0 and get_prefijo(cursos[j].clave, 4) == 'TGTI']) >= 0, "min_tutoria_individual_para_el_profe_"+str(i))

# Las tutorias no pueden darse ni en la primera ni en la última hora del turno

for g in range(0, G):
    for d in range(0, D):
        for tr in range(0, len(turnos)):
            if busca_turno(turnos[tr].grupos, grupos[g].nombre):
                mod.addConstraint(lpSum([st[g, t, d] for t in turnos[tr].horas])
                                  == 1, "solo_una_hora_inicio_"+str(g)+"_"+str(d))
                mod.addConstraint(lpSum([fin[g, t, d] for t in turnos[tr].horas]) == 1, "solo_una_hora_fin_"+str(g)+"_"+str(d))
                mod.addConstraint(lpSum([st[g, t, d] for t in turnos[tr].horas_comp]) == 0, "no_solo_una_hora_inicio_"+str(g)+"_"+str(d))
                mod.addConstraint(lpSum([fin[g, t, d] for t in turnos[tr].horas_comp]) == 0, "no_solo_una_hora_fin_"+str(g)+"_"+str(d))
                for t in turnos[tr].horas_comp:
                    mod.addConstraint(
                        xt[g, t, d] <= 0, "no_activa_hora_"+grupos[g].nombre+"_"+str(t)+"_"+str(d))

for g in range(0, G):
    for d in range(0, D):
        for t in range(0, T):
            if t == 0:
                mod.addConstraint(st[g, t, d] >= xt[g, t, d])
            else:
                mod.addConstraint(st[g, t, d] >= xt[g, t, d]-xt[g, t-1, d])
                mod.addConstraint(fin[g, t, d] >= -xt[g, t, d]+xt[g, t-1, d])


for g in range(0, G):
    for t in range(0, T):
        for d in range(0, D):
            mod.addConstraint(lpSum([x[i, j, t, d] for i in range(0, N) for j in grupos[g].cursos if get_prefijo(cursos[j].clave, 4) != "TGTI"]) >= 1 - 10000*(1-st[g, t, d]), "debe_iniciar"+"_"+grupos[g].nombre+"_"+str(t)+"_"+str(d))
            mod.addConstraint(st[g, t, d]+fin[g, t, d] <= 1)
        #	mod.addConstraint( lpSum( [ x[i,j,t,d] for i in range(0,N) for j in grupos[g].cursos if cursos[j].clave!="TGTI"]) >= 1 - 10000*(1-fin[g,t,d]),"debe_fin"+"_"+grupos[g].nombre+"_"+str(t)+"_"+str(d))

for i in range(0, N):
    for g in range(0, G):
        for j in grupos[g].cursos:
            for tr in range(0, len(turnos)):
                if busca_turno(turnos[tr].grupos, grupos[g].nombre):
                    for t in turnos[tr].horas:
                        for d in range(0, D):
                            mod.addConstraint(x[i, j, t, d] <= xt[g, t, d], "activa_hora_"+str(i)+"_"+grupos[g].nombre+"_"+str(j)+"_"+str(t)+"_"+str(d))


for t in range(0, T):
    for d in range(0, D):
        mod.addConstraint(lpSum([x[i, j, t, d] for i in range(0, N) for j in range(0, M)]) <= 8, "max_hrs_simultaneas_"+str(d)+"_"+str(t))


# for i in range(0,N):
# if profesores[i].clave!='99' and profesores[i].clave!='-1' and profesores[i].contrato=='Base' and i==1:
# for j in range(0,M):
# if cursos[j].fijo==0 and cursos[j].clave=='TGTI':
# for g in range(0,G):
# if cursos[j].gr==grupos[g].nombre:
#						mod.addConstraint( y[i,j]  <=  lpSum( [ y[i,q] for q in grupos[g].cursos if cursos[q].clave!="TGTI" and cursos[q].fijo==0] ), "tutor_solo_si_grupo_"+str(i)+"_"+grupos[g].nombre)


# profesores[i].dias_idx[d][t]
#mod.writeLP("tt_upmh.lp")
#mod.solve(COIN(msg=1,timeLimit=8*3600,options=["cuts off","presolve on","passPresolve 5","strong 1","CostStrategy priorities","FeasibilityPump off","VndVariableNeighborhoodSearch on"]))
# mod.solve(COIN_CMD(msg=1,timeLimit=3600))
mod.solve(GUROBI_CMD(msg=1,timeLimit=3600))
# mod.solve(GLPK_CMD(msg=1,timeLimit=3600))
# mod.solve(LpSolver_CMD(path="/usr/bin/lp_solve"))
# mod.solve(SCIP_CMD(path="/usr/bin/scip"))
#mod.solve(CPLEX(msg=1,timeLimit=2800))
#mod.solve(MOSEK(msg=1,options = {mosek.dparam.mio_max_time:1300}))
#mod.solve(HiGHS_CMD(msg=1, timeLimit=11*1800))

fh_resultados = open(nombre+"_out.csv", "w")
fh_resultados.write("Clave,Grupo,Materia,Profesor,Preferencia,Lunes,Martes,Miercoles,Jueves,Viernes\n")
for i in range(0, N):
    for j in range(0, M):
        if abs(y[i, j].varValue) > 0.00001:
            fh_resultados.write(cursos[j].clave + "," + cursos[j].gr +
                                "," + cursos[j].nombre + "," + profesores[i].nombre+",")
            if len(cursos[j].preferencias) > 0:
                for p in range(0, len(cursos[j].preferencias)):
                    fh_resultados.write(cursos[j].preferencias[p]+" ")
            else:
                fh_resultados.write("-")
            fh_resultados.write(",")
            for d in range(0, D):
                semana = []
                for t in range(0, T):
                    if abs(x[i, j, t, d].varValue) > 0.00001:
                        semana.append(t)
                if len(semana) > 0:
                    # print(j,cursos[j].gr,semana)
                    fh_resultados.write(
                        str(semana[0]+7)+"-"+str(semana[len(semana)-1]+8))
                else:
                    fh_resultados.write("-")
                fh_resultados.write(",")
            fh_resultados.write("\n")
fh_resultados.close()
indice_c=0.0
n_cursos=0.0
for i in range(0, N):
    r=imprime_profesor(nombre, i, profesores, cursos, x, T, D)
    if r[0]>0 or r[1]>0    :
        indice_c+=r[0]
        n_cursos+=1
        print(i,",",profesores[i].nombre,",",r[0],",",r[1])
print(indice_c/n_cursos)

for g in range(0, G):
    imprime_grupo(nombre, g, grupos, cursos, x, N, T, D)

# for g in range(0,G):
# for t in range(0,T):
# for d in range(0,D):
# if abs(st[g,t,d].varValue)>0.001:
# print("inicio",g,t,d)
# for g in range(0,G):
# for t in range(0,T):
# for d in range(0,D):
# if abs(fin[g,t,d].varValue)>0.001:
# print("fin",g,t,d)
#
# for g in range(0,G):
# for t in range(0,T):
# for d in range(0,D):
# if abs(xt[g,t,d].varValue)>0.001:
# print("xt",g,t,d)
