#!/usr/bin/python3
import sys
import random
import os
from pulp import *

class curso:
	def __init__(self,clave,gr,nombre,profesor,preferencias,horario={}):
		self.clave=clave
		self.gr=gr
		self.nombre=nombre
		self.profesor=profesor
		self.dias={}
		self.sesion_len={}
		self.ub={}
		self.lb={}
		self.prefs=preferencias
		for d in range(0,5):
			for t in range(0,14):
				self.dias[d,t]=0
		for d in range(0,5):
			if (horario[d] !='') and (horario[d] != '-') and (horario[d] != '-\n'):
				#print(horario[d])
				dia=horario[d].split("-")
				lb=int(dia[0])
				ub=int(dia[1])
				self.sesion_len[d]=ub-lb
				self.lb[d]=lb
				self.ub[d]=ub
				for t in range(0,14):
					if (t+7)>=lb and (t+7)<ub:
						self.dias[d,t]=1
			else:
				self.sesion_len[d]=0
				self.lb[d]=0
				self.ub[d]=0
	def get_costo_pref(self,salon):
		for k in range(0,len(self.prefs)):
			if salon==self.prefs[k]:
				return k+1	
				break
		return 100
			
			


class grupo:
	def __init__(self,nombre):
		self.nombre=nombre
		self.cursos=[]
		self.capacidad=0
	def add_curso(self,curso):
		self.cursos.append(curso)	
	def update_capacidad(self,capacidad):
		self.capacidad=capacidad


class salon:
	def __init__(self,nombre,capacidad):
		self.nombre=nombre
		self.capacidad=capacidad

def busca_grupo(grupos,gr):
	for i in range(0,len(grupos)):
		if gr.nombre==grupos[i].nombre:
			return i
			break
	return -1

def busca_grupo2(grupos,gr):
	for i in range(0,len(grupos)):
		if grupos[i].nombre==gr:
			return i
			break
	return -1


def fobj1(grupos,z,G,S,D):
	suma=0
	for g in range(0,G):
		for p in grupos[g].cursos:
			for q in grupos[g].cursos:
				if p!=q:
					for j in range(0,S):
						for d in range(0,D):
							suma+=z[p,q,j,d]
							#print(grupos[g].nombre,p,q,j,d)
	
	return suma


def fobj3(grupos,cursos,salones,y,G,C,S,D):
	suma=0
	for g in range(0,G):
		for i in grupos[g].cursos:
			for j in range(0,S):
				for d in range(0,D):
					suma+=(grupos[g].capacidad / salones[j].capacidad)*y[i,j,d]
	return suma


def fobj4(cursos,salones,y,G,C,S,D):
	suma=0
	for g in range(0,G):
		for i in grupos[g].cursos:
			for j in range(0,S):
				for d in range(0,D):
					suma += cursos[i].get_costo_pref(salones[j].nombre) * y[i,j,d]

	return suma



def imprime_grupo(g,grupos,cursos,x,S,T,D):
	fh_horario_grupo=open("grupo_"+str(g)+".csv","w")
	fh_horario_grupo.write("Horario del grupo "+grupos[g].nombre+"\n \n")
	fh_horario_grupo.write("Hora/Dia,Lunes,Martes,Miercoles,Jueves,Viernes\n")
	for t in range(0,T):
		fh_horario_grupo.write(str(t+7)+"-"+str(t+8)+",")
		for d in range(0,D):
			for i in grupos[g].cursos:
				for j in range(0,S):
					if abs(x[i,j,t,d].varValue)>0.0001:
						fh_horario_grupo.write(cursos[i].clave+":"+"Salon "+ str(j))
			fh_horario_grupo.write(",")
		fh_horario_grupo.write("\n")
	fh_horario_grupo.close()

def imprime_salon(s,cursos,x,C,T,D):
	fh_salon=open("salon_"+str(s)+".csv","w")
	fh_salon.write("Horario del salon "+str(s)+"\n \n")
	fh_salon.write("Hora/Dia,Lunes,Martes,Miercoles,Jueves,Viernes\n")
	for t in range(0,T):
		fh_salon.write(str(t+7)+"-"+str(t+8)+",")
		for d in range(0,D):
			for i in range(0,C):
				if abs( x[i,j,t,d].varValue )>0.0001:
					fh_salon.write(cursos[i].clave+"-"+cursos[i].gr)
			fh_salon.write(",")
		fh_salon.write("\n")
	fh_salon.close()			



def dibujar_dia(cursos,grupos,x,d,C,T,S,G):
	fh_dia=open("dia_"+str(d)+".tex","w")
	fh_dia.write("\\documentclass{standalone} \n")
	fh_dia.write("\\usepackage[usenames,dvipsnames]{xcolor} \n")
	fh_dia.write("\\usepackage{tikz}\n")
	fh_dia.write("\\usetikzlibrary{patterns} \n")
	random.seed(126)
	rgbt = [((random.uniform(0,1)+random.uniform(0,1)+random.uniform(0,1) )/3.0,random.uniform(0,1), (random.uniform(0,1)+random.uniform(0,1))/2.0) for g in range(G)]
	semana=["Lunes","Martes","Miercoles","Jueves","Viernes"]
	for g in range(0,G):
		fh_dia.write("\\definecolor{col"+str(g)+"}{rgb}{"+ str(rgbt[g][0]) +","+ str(rgbt[g][1]) +","+ str(rgbt[g][2]) +"}\n")
	fh_dia.write("\\begin{document} \n")
	fh_dia.write("\\begin{tikzpicture} \n")	
	fh_dia.write("\\draw[-latex,line width=0.6 mm,draw=black, opacity=0.9] (0,0) -- (15,0);")
	fh_dia.write("\\draw[-latex,line width=0.6 mm,draw=black, opacity=0.9] (0,0) -- (0,"+str(S+1)+");")
	fh_dia.write( "\\node[font=\\fontsize{14pt}{14pt}] at (7.5,"+ str(S+2)+"){"+ semana[d] +"};\n")
	for t in range(0,T+1):
		fh_dia.write( "\\node[font=\\fontsize{8}{8}] at (" + str(t)+ ",-0.5){$"+str(t+7)+"$};\n")
		fh_dia.write("\\draw[line width=0.5 mm]("+str(t)+",-0.3)--("+str(t)+",0.1);")

	for s in range(0,S):
		fh_dia.write(  "\\node[font=\\fontsize{8}{8}] at (-0.6," +str(s+0.5)+"){$s_{"+str(s)+"}$};\n")	
		fh_dia.write("\\draw[line width=0.5 mm](-0.4,"+str(s+1)+")--(0.2,"+str(s+1)+");")

	for s in range(0,S):
		for t in range(0,T):
			for g in range(0,G):
				for i in grupos[g].cursos:
					if abs(x[i,s,t,d].varValue)>0.0001:
						fh_dia.write("\\fill[line width=0.2 mm,fill=col"+str(g)+", opacity=0.5]("+ str(t+0.01)+","+str(s+0.01)+") rectangle("+ str(t+1-0.01)+","+str(s+1-0.01)+");\n" )
						fh_dia.write("\\node[font=\\fontsize{8}{8}] at (" + str(t+0.5) + ","+str(s+0.5) +"){"+grupos[g].nombre+"};\n" )
	# ("+str(j)+","+str(self.m-(i+1))+") rectangle ( " +str(j+1) +","+str(self.m-i)+");\n")
	fh_dia.write("\\end{tikzpicture}\n")
	fh_dia.write("\\end{document}\n")
	fh_dia.close()		
	os.system("pdflatex --interaction=batchmode " + "dia_"+str(d) + ".tex")	



def dibujar_dia2(cursos,grupos,salones,y,d,C,T,S,G):
	fh_dia=open("dia_"+str(d)+".tex","w")
	fh_dia.write("\\documentclass{standalone} \n")
	fh_dia.write("\\usepackage[usenames,dvipsnames]{xcolor} \n")
	fh_dia.write("\\usepackage{tikz}\n")
	fh_dia.write("\\usetikzlibrary{patterns} \n")
	random.seed(127)
	rgbt = [((random.uniform(0,1)+random.uniform(0,1)+random.uniform(0,1) )/3.0,random.uniform(0,1), (random.uniform(0,1)+random.uniform(0,1))/2.0) for g in range(G)]
	semana=["Lunes","Martes","Miercoles","Jueves","Viernes"]
	for g in range(0,G):
		fh_dia.write("\\definecolor{col"+str(g)+"}{rgb}{"+ str(rgbt[g][0]) +","+ str(rgbt[g][1]) +","+ str(rgbt[g][2]) +"}\n")
	fh_dia.write("\\begin{document} \n")
	fh_dia.write("\\begin{tikzpicture} \n")	
	fh_dia.write("\\draw[-latex,line width=0.6 mm,draw=black, opacity=0.9] (0,0) -- (15,0);")
	fh_dia.write("\\draw[-latex,line width=0.6 mm,draw=black, opacity=0.9] (0,0) -- (0,"+str(S+1)+");")
	fh_dia.write( "\\node[font=\\fontsize{14pt}{14pt}] at (7.5,"+ str(S+2)+"){"+ semana[d] +"};\n")
	for t in range(0,T+1):
		fh_dia.write( "\\node[font=\\fontsize{8}{8}] at (" + str(t)+ ",-0.5){$"+str(t+7)+"$};\n")
		fh_dia.write("\\draw[line width=0.5 mm]("+str(t)+",-0.3)--("+str(t)+",0.1);")

	for s in range(0,S):
		fh_dia.write(  "\\node[font=\\fontsize{8}{8}] at (-0.6," +str(s+0.5)+"){$"+ salones[s].nombre + "$};\n")	
		fh_dia.write("\\draw[line width=0.5 mm](-0.4,"+str(s+1)+")--(0.2,"+str(s+1)+");")

	for s in range(0,S):
		for g in range(0,G):
			for i in grupos[g].cursos:
				if abs(y[i,s,d].varValue)>0.0001:
					fh_dia.write("\\fill[line width=0.2 mm,fill=col"+str(g)+", opacity=0.3]("+ str( cursos[i].lb[d]-7 +0.01)+","+str(s+0.01)+") rectangle("+ str(cursos[i].ub[d]-7-0.01)+","+str(s+1-0.01)+");\n" )
					fh_dia.write("\\node[font=\\fontsize{6}{6}] at (" + str( ((cursos[i].lb[d]-7) + (cursos[i].ub[d]-7))*0.5) + ","+str(s+0.3) +"){$"+grupos[g].nombre+"$};\n"  )
					fh_dia.write("\\node[font=\\fontsize{6}{6}] at (" + str( ((cursos[i].lb[d]-7) + (cursos[i].ub[d]-7))*0.5) + ","+str(s+0.7) +"){$"+cursos[i].clave+"$};\n"  )
	fh_dia.write("\\end{tikzpicture}\n")
	fh_dia.write("\\end{document}\n")
	fh_dia.close()		
	os.system("pdflatex --interaction=batchmode " + "dia_"+str(d) + ".tex")	

def dibujar_salon(cursos,grupos,salones,j,y,D,C,G,T):
	fh_salon=open("salon_"+salones[j].nombre+".tex","w")
	fh_salon.write("\\documentclass{standalone} \n")
	fh_salon.write("\\usepackage[usenames,dvipsnames]{xcolor} \n")
	fh_salon.write("\\usepackage{tikz}\n")
	fh_salon.write("\\usetikzlibrary{patterns} \n")
	random.seed(127)
	rgbt = [((random.uniform(0,1)+random.uniform(0,1)+random.uniform(0,1) )/3.0, random.uniform(0,1) ,  (random.uniform(0,1)+random.uniform(0,1))/2.0) for g in range(G)]
	for g in range(0,G):
		fh_salon.write("\\definecolor{col"+str(g)+"}{rgb}{"+ str(rgbt[g][0]) +","+ str(rgbt[g][1]) +","+ str(rgbt[g][2]) +"}\n")
	semana=["Lunes","Martes","Miercoles","Jueves","Viernes"]
	fh_salon.write("\\begin{document} \n")
	fh_salon.write("\\begin{tikzpicture} \n")	
	fh_salon.write("\\node[font=\\fontsize{6}{6}] at("+str(4.5)+ ", 1.0 ){Horario del salón " + salones[j].nombre + "};\n")
	
	
	
	
	fh_salon.write("\\draw[line width=0.25 mm,opacity=0.5](0, 0 )--("+str(10) +", 0);")   
	fh_salon.write("\\draw[line width=0.25 mm,opacity=0.5](0," + str(-T) +")--("+ str(10) + "," +str(-T)+ ");")   
	for d in range(0,D+1):
		if d<D:
			fh_salon.write("\\node[font=\\fontsize{6}{6}] at("+str((d*2)+1)+ ", 0.5){$"+semana[d]+"$};\n")
			fh_salon.write("\\draw[line width=0.25 mm,opacity=0.5](" + str(2*d)+ ", 0 )--(" +str(2*d)+ ","+str(-T)+");\n")
		else:
			fh_salon.write("\\draw[line width=0.25 mm,opacity=0.5](" + str(2*d)+ ", 0 )--(" +str(2*d)+ ","+str(-T)+");\n")   

	for t in range(0,T+1):
		fh_salon.write( "\\node[font=\\fontsize{6}{6}] at (-0.6," + str(-t) + "){$"+str(t+7)+":00$};\n")
		fh_salon.write("\\draw[line width=0.2 mm, opacity=0.5](-0.2,"+str(-t)+")--(0,"+str(-t)+");\n")

	for g in range(0,G):
		for i in grupos[g].cursos:
			for d in range(0,D):
				if abs(y[i,j,d].varValue)>0.0001:
						fh_salon.write("\\fill[line width=0.1 mm,fill=col"+str(g)+", opacity=0.2]("+ str(2*d+0.02) +","+   str( -(cursos[i].lb[d]-7 + 0.02) )+") rectangle("+ str(2*(d+1)-0.02) +","+str(-(cursos[i].ub[d]-7-0.02))+");\n" )
						fh_salon.write("\\node[font=\\fontsize{6}{6}] at (" + str( 2*d+1 ) + ","+str(-0.2 + (- 0.5 * (cursos[i].lb[d]+cursos[i].ub[d]-14) )) +"){$"+grupos[g].nombre+"$};\n"  )
						fh_salon.write("\\node[font=\\fontsize{6}{6}] at (" + str( 2*d+1 ) + ","+str(+0.2 + (- 0.5 * (cursos[i].lb[d]+cursos[i].ub[d]-14) ) ) +"){$"+cursos[i].clave + "$};\n"  )
						#fh_salon.write("\\node[font=\\fontsize{6}{6}] at (" + str( 2*d+1 ) + ","+str(-0.4 + (- 0.5 * (cursos[i].lb[d]+cursos[i].ub[d]-14) ) ) +"){$"+ str(round(grupos[g].capacidad / salones[j].capacidad,3)) + "$};\n"  )
	fh_salon.write("\\end{tikzpicture}\n")
	fh_salon.write("\\end{document}\n")
	fh_salon.close()
	os.system("pdflatex --interaction=batchmode "+ "salon_"+salones[j].nombre+".tex")

def imprime_informe(cursos,grupos,salones,x,y,D,C,G,T):
	fh_informe=open("informe.csv","w")
	fh_informe.write("Clave,Grupo,Curso,Profesor,Lunes,Martes,Miercoles,Jueves,Viernes,L-rho,M-rho,Mi-rho,Ju-rho,Vi-rho,L-phi,M-phi,Mi-phi,Ju-Phi,Vi-Phi\n")
	for i in range(0,C):
		fh_informe.write(cursos[i].clave+","+cursos[i].gr+","+cursos[i].nombre+","+cursos[i].profesor+",")
		for d in range(0,D):
			if cursos[i].lb[d]==0 and cursos[i].ub[d]==0:
				fh_informe.write("-,")
			else: 
				fh_informe.write(str(cursos[i].lb[d])+"--"+str(cursos[i].ub[d])+",")
		for d in range(0,D):
			if cursos[i].sesion_len[d]==0:
				fh_informe.write("0.0,")	
			for j in range(0,S):
				if abs(y[i,j,d].varValue)>0.0001 and cursos[i].sesion_len[d]>0:
					fh_informe.write(str( round(grupos[busca_grupo2(grupos,cursos[i].gr)].capacidad / salones[j].capacidad,3))+",")
		for d in range(0,D):
			if cursos[i].sesion_len[d]==0:
				fh_informe.write("0.0,")	
			for j in range(0,S):
				if abs(y[i,j,d].varValue)>0.0001 and cursos[i].sesion_len[d]>0:
					fh_informe.write(str( round(cursos[i].get_costo_pref(salones[j].nombre),3))+",")			
		fh_informe.write("\n")
	fh_informe.close()

cursos=[]
grupos={}
salones=[]

fh_cursos=open(sys.argv[1],"r")
fh_grupos=open(sys.argv[2],"r")
fh_salones=open(sys.argv[3],"r")

l=0
g=0
for linea in fh_cursos:
	if l==0:
		l=l+1
	else:	
		l_list=linea.split(",")
		pref=l_list[4]
		if pref=="-":
			preferencias=[]
		else:
			preferencias=pref.split(" ")
		horario=[l_list[5],l_list[6],l_list[7],l_list[8],l_list[9]]
		c=curso(l_list[0],l_list[1],l_list[2],l_list[3],preferencias,horario)
		cursos.append(c)
		gr=grupo(l_list[1])
		indice_g=busca_grupo(grupos,gr)
		if(indice_g==-1):
			grupos[g]=gr
			grupos[g].add_curso(len(cursos)-1)
			g=g+1
		else:
			grupos[indice_g].add_curso(len(cursos)-1)	
		l=l+1
fh_cursos.close()
l=0
for linea in fh_grupos:
	if l==0:
		l=l+1
	else:
		sl=linea.strip()
		s=sl.split(",")
		idx=busca_grupo2(grupos,s[0])
		grupos[idx].update_capacidad(int(s[1]))
		l=l+1

fh_grupos.close()

l=0
for linea in fh_salones:
	if l==0:
		l=l+1
	else:
		sl=linea.strip()
		s=sl.split(",")
		salones.append(salon(s[0],int(s[1])))
		l=l+1

fh_salones.close()




C=len(cursos)
G=len(grupos)
S=len(salones)
T=14
D=5

mod=LpProblem(sense=LpMinimize)


x={}
for i in range(0,C):
	for j in range(0,S):
		for t in range(0,T):
			for d in range(0,D):
				x[i,j,t,d]=LpVariable("x"+"_"+str(i)+"_"+str(j)+"_"+str(t)+"_"+str(d),0,1,LpInteger)
				#LpVariable("x"+"_"+str(i)+"_"+str(j)+"_"+str(t)+"_"+str(d),0,1,LpInteger)


y={}
r={}
f={}
for i in range(0,C):
	for j in range(0,S):
		for d in range(0,D):
			y[i,j,d]=LpVariable("y"+"_"+str(i)+"_"+str(j)+"_"+str(d),0,1,LpInteger)
			

for d in range(0,D):
	r[d]=LpVariable("r_"+str(d),0,None,LpInteger)
	for j in range(0,S):
		f[d,j]=LpVariable( "f_"+str(d)+"_"+str(j) ,0,1,LpBinary )

z={}
for g in range(0,G):
	for p in grupos[g].cursos:
		for q in grupos[g].cursos:
			if p!=q:
				for j in range(0,S):
					for d in range(0,D):
						z[p,q,j,d] = LpVariable("z_"+str(p)+"_"+str(q)+"_"+str(j)+"_"+str(d),0,1,LpInteger)


#for i in range(0,C):
#	for t in range(0,T):
#		for d in range(0,D):
#			mod.add_constr(  milp.xsum( x[i,j,t,d] for j in range(0,S))  == 1 ,"Un_curso_"+str(i)+"_"+str(t)+"_"+str(d)+"_necesita_un_salon" )		



f1=fobj1(grupos,z,G,S,D)
f3=fobj3(grupos,cursos,salones,y,G,C,S,D)
f4=fobj4(cursos,salones,y,G,C,S,D)
mod.setObjective(10*f4+100*f3+100*lpSum([r[d] for d in range(0,D)])-f1)

for i in range(0,C):
	for d in range(0,D):
		if cursos[i].sesion_len[d]>0:
			mod.addConstraint(lpSum([y[i,j,d] for j  in range(0,S)]) ==1,"un_curso_debe_tener_un_salon_"+str(i)+"_"+str(d) )
		else:
			mod.addConstraint(lpSum([y[i,j,d] for j  in range(0,S)]) ==0,"un_curso_no_debe_tener_un_salon_"+str(i)+"_"+str(d) )

#print(x)
for i in range(0,C):
	for j in range(0,S):
		for d in range(0,D):
			mod.addConstraint(y[i,j,d] <= f[d,j])


for j in range(0,S):
	for t in range(0,T):
		for d in range(0,D):
			mod.addConstraint(  lpSum([x[i,j,t,d] for i in range(0,C)]) <=1,"Un_salon_puede_tener_a_lo_mas_un_curso_"+str(j)+"_"+str(t)+"_"+str(d))


for d in range(0,D):
	mod.addConstraint( lpSum([f[d,j] for j in range(0,S)])  <= r[d],"maximos_salones_por_dia_"+str(d) )


for j in range(0,S):
	for d in range(0,D):
		for t in range(0,T):
			mod.addConstraint( lpSum([y[i,j,d]  for i in range(0,C) if cursos[i].dias[d,t]==1]) <=1 ,"traslape_a_la_hora_"+str(t)+"_del_dia_"+str(d)+"_en_el_salon"+str(j))


for i in range(0,C):
	for d in range(0,D):
		for j in range(0,S):	
				mod.addConstraint( lpSum( [x[i,j,t,d] for t in range(0,T) if cursos[i].dias[d,t] == 1 ] ) == cursos[i].sesion_len[d] * y[i,j,d] ,"toda_la_sesion_"+str(i)+"_"+str(j)+"_"+str(d))
			#else:
			#	mod.add_constr( milp.xsum( x[i,j,t,d] for t in range(0,T) if cursos[i].dias[d,t] == 0 ) ==  0,"toda_la_sesion_"+str(i)+"_"+str(j)+"_"+str(d))
#				for t in range(0,T):
#					mod.add_constr(x[i,j,t,d]>=y[i,j,d],"toda_la_sesion_"+str(i)+"_"+str(j)+"_"+str(d)+"_"+str(t))	

#for g in range(0,G):
#	for p in range(0,len(grupos[g].cursos)-1):
#		p1=grupos[g].cursos[p]
#		q=grupos[g].cursos[p+1]
#		for d in range(0,D):
#			if cursos[p1].sesion_len[d]>0 and cursos[q].sesion_len[d]>0:
#				for j in range(0,S):
#					print(d,j,p1,q)
#					mod.add_constr(y[p1,j,d]==y[q,j,d],"mismo_salon_cursos_grupo_"+str(g)+"_"+str(p1)+"_"+str(q)+"_"+str(j)+"_"+str(d))

#for g in range(0,G):
#	for p in grupos[g].cursos:
#		for q in grupos[g].cursos:
#			if p<q:
#				for j in range(0,S):
#					for d in range(0,D):
#						if cursos[p].sesion_len[d]>0 and cursos[q].sesion_len[d]>0:
							#print(d,j,p,q)
#							mod.add_constr(y[p,j,d]==y[q,j,d],"mismo_salon_cursos_grupo_"+str(g)+"_"+str(p)+"_"+str(q)+"_"+str(j)+"_"+str(d))

for g in range(0,G):
	for p in grupos[g].cursos:
		for q in grupos[g].cursos:
			if p!=q:
				for j in range(0,S):
					for d in range(0,D):
						mod.addConstraint(z[p,q,j,d] <= y[p,j,d])
						mod.addConstraint(z[p,q,j,d] <= y[q,j,d])
						mod.addConstraint( y[p,j,d] + y[q,j,d] <=  z[p,q,j,d] + 1  )


mod.writeLP("tt_upmh_ca.lp")
mod.solve(HiGHS_CMD(msg=1,timeLimit=1*1800))
#mod.solve(GUROBI_CMD(msg=1,timeLimit=800))

#for i in range(0,C):
#	for j in range(0,S):
#		for d in range(0,D):
#			if abs(y[i,j,d].x)>0.00001:
#				print("y",i,j,d)

#for i in range(0,C):
#	for j in range(0,S):
#		for t in range(0,T):
#			for d in range(0,D):
#				if abs(x[i,j,t,d].x)>0.00001:
#					print("x",i,j,t,d)

for g in range(0,G):
	imprime_grupo(g,grupos,cursos,x,S,T,D)					

for j in range(0,S):
	imprime_salon(j,cursos,x,C,T,D)
	dibujar_salon(cursos,grupos,salones,j,y,D,C,G,T)

for d in range(0,D):
	dibujar_dia2(cursos,grupos,salones,y,d,C,T,S,G)



imprime_informe(cursos,grupos,salones,x,y,D,C,G,T)