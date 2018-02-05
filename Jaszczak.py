import numpy as np
import pylab as py
import os
import Image as im

A=421.63 #aktywnosc w fantomie
npix=128. #podaj liczbe pikseli
zoom=[['2',290],['1.33',430],['1.66',360]] # mozna dopisac wiecej

Scale=npix/zoom[2][1]  # [ktory zoom z listy] [zawsze 1-ktora liczba z listy]
Dtype="float32" #typ zmiennych wyjsciowych 'float'. Mozna zmienic.

#wsp osl
wsp_osl_plex=0.130/Scale/10
wsp_osl_woda=0.120/Scale/10

#wymiary walca [mm]
d1=206
d2=220
h1=186
h2=200
offset=npix-Scale*d2+1 #piksele wokol walca

#wymiary cyl [mm] #zamieniajac pozycje w kazdym elemencie zamieniamy miejscami cylindry.
# Miejsce 1 jest na godzinie 3 cylindra. [1,2,3,4,5,6]
D_cyl1=[28,14,22,28,14,22]
D_cyl2=[34,20,28,34,20,28]
H_cyl1=[32,18,26,32,18,26]
H_cyl2=[40,26,34,40,26,34]
A_cyl=[2.86,0.67,1.53,0.0,0.4,2.04] #aktywnosci zrodel

H_cyl_rods=6

#wymiary pretow [mm]
D_rods=6
h_rods=h2/2+np.array(H_cyl2)/2.


#skala i wymiary macierzy wynikowej

Size_X=int((d2)*Scale)
Size_Y=int((d2)*Scale) # Liczba pixeli w danym wymiarze to Size_N*Scale
Size_Z=int((d2)*Scale)

#poczatkowe punkty walca [mm]

x0_cyl=Size_X/2/Scale
y0_cyl=Size_Y/2/Scale
z0_cyl=Size_Z/2/Scale-h2/2

#poczatkowe polozenia katowe cylindrow i pretow [rad]
#UHR
#fi=[2.6,(np.pi/3)+2.6,(np.pi*2/3)+2.6,(np.pi)+2.6,(np.pi*4/3)+2.6,(np.pi*5/3)+2.6]
#HR
fi=[1.35,(np.pi/3)+1.35,(np.pi*2/3)+1.35,(np.pi)+1.35,(np.pi*4/3)+1.35,(np.pi*5/3)+1.35]
#AP
#fi=[+2.4,(np.pi/3)+2.4,(np.pi*2/3)+2.4,(np.pi)+2.4,(np.pi*4/3)+2.4,(np.pi*5/3)+2.4]

#poczatkowe punkty pretow [mm]

x0_rods=Size_X/2/Scale
y0_rods=Size_Y/2/Scale
z0_rods=Size_Z/2/Scale-h2/2

#poczatkowe punkty cylindrow[mm]
x0_sph=Size_X/2/Scale
y0_sph=Size_Y/2/Scale
z0_sph=Size_Z/2/Scale-h2/2


#funkcja szukajaca punktow w ktorych jest material walca
def drawCyl(d1,d2,h1,h2,x0,y0,z0,Scale):
    d1=int(d1*Scale)
    d2=int(d2*Scale)
    h1=int(h1*Scale)
    h2=int(h2*Scale)
    x0=int(x0*Scale)
    y0=int(y0*Scale)
    z0=int(z0*Scale)
    Cyl=[]
    r12=(d1/2)**2
    r22=(d2/2)**2
    for x in range(-d2/2,d2/2):
        x2=x**2
        for y in range(-d2/2,d2/2):
            y2=y**2
            for z in range(h2):
                req1=x2 + y2
                req2=z<=(h2-h1)/2
                req3=z>=h1+(h2-h1)/2
                req4=z<=h2
                req5=req3 and req4
                req6=req2 or req5
                if req1<=r22 and req6:
                    Cyl.extend([(z+z0,x+x0,y+y0)])
                if req1>=r12 and req1<=r22 and not req2 and not req3:
                    Cyl.extend([(z+z0,x+x0,y+y0)])
    return Cyl

def drawCyl2(d1,d2,h1,h2,x0,y0,z0,Scale):
    d1=int(d1*Scale)
    d2=int(d2*Scale)
    h1=int(h1*Scale)
    h2=int(h2*Scale)
    x0=int(x0*Scale)
    y0=int(y0*Scale)
    z0=int(z0*Scale)
    Cyl=[]
    r12=(d1/2)**2
    r22=(d2/2)**2
    for x in range(-d2/2,d2/2):
        x2=x**2
        for y in range(-d2/2,d2/2):
            y2=y**2
            for z in range(h2):
                req1=x2 + y2
                req2=z<=(h2-h1)/2-1
                req3=z>=h1+(h2-h1)/2-1
                req4=z<=h2+1
                req5=req3 and req4
                req6=req2 or req5
                if req1<=r22 and req6:
                    Cyl.extend([(z+z0,x+x0,y+y0)])
                if req1>=r12 and req1<=r22 and not req2 and not req3:
                    Cyl.extend([(z+z0,x+x0,y+y0)])
    return Cyl

#funkcja szukajaca punktow w ktorych jest material pretow
def drawRod(d,h,x0,y0,z0,Scale):
    d=int(d*Scale)
    h=int(h*Scale)
    x0=int(x0*Scale)
    y0=int(y0*Scale)
    z0=int(z0*Scale)
    Rod=[]
    r2=(d/2)**2
    for x in range(-d/2,d/2):
        x2=x**2
        for y in range(-d/2,d/2):
            y2=y**2
            for z in range(h):
                req1=x2 + y2
                if req1<=r2 and z<=h:
                    Rod.extend([(z+z0,x+x0,y+y0)])
    return Rod


#szukanie punktow walca
mainCyl=drawCyl(d1,d2,h1,h2,x0_cyl,y0_cyl,z0_cyl,Scale)

main_cyl_fill=[]
main_cyl_fill.extend(drawRod(d1,h1,x0_cyl,y0_cyl,z0_cyl+(h2-h1)/2,Scale))

#szukanie punktow pretow
Rods=[]
for n in range(len(h_rods)):
    Rods.extend(drawRod(D_rods,h_rods[n],x0_rods+d2/4.*np.sin(fi[n]),y0_rods+d2/4.*np.cos(fi[n]),z0_rods,Scale))

#szukanie punktow aktywnosci
Cyl_A=[]
N_Cyl_A=[]

for n,d in enumerate(D_cyl1):
    Cyl_A.extend(drawRod(d,H_cyl1[n],x0_rods+d2/4.*np.sin(fi[n]),y0_rods+d2/4.*np.cos(fi[n]),z0_sph+h_rods[n]+H_cyl_rods,Scale))
    N_Cyl_A.append(len(Cyl_A))

#szukanie punktow cylindrow
Cylinder=[]

for n in range(len(D_cyl1)):
    Cylinder.extend(drawCyl2(D_cyl1[n],D_cyl2[n],H_cyl1[n],H_cyl2[n],x0_sph+d2/4.*np.sin(fi[n]),y0_sph+d2/4.*np.cos(fi[n]),z0_sph+h_rods[n],Scale))


#macierz wynikowa wsp oslabienia
M=np.zeros((Size_X+offset,Size_Y+offset,Size_Z+offset),dtype=Dtype)

#wpisywanie wsp oslabienia w komorki macierzy wynikowej M

for nr,i in enumerate(main_cyl_fill):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=wsp_osl_woda
##    if nr%1000==0:
##        print "Cylinders", float(nr)/len(main_cyl_fill)

for nr,i in enumerate(Cyl_A):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=wsp_osl_woda
##    if nr%1000==0:
##        print "Cylinders", float(nr)/len(Cyl_A)

for nr,i in enumerate(mainCyl):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=wsp_osl_plex
##    if nr%10000==0:
##        print "mainCyl", float(nr)/len(mainCyl)

for nr,i in enumerate(Rods):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=wsp_osl_plex
##    if nr%1000==0:
##        print "Rods", float(nr)/len(Rods)

for nr,i in enumerate(Cylinder):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=wsp_osl_plex
##    if nr%1000==0:
##        print "Cylinder", float(nr)/len(Cylinder)

#zapisywanie wyniku do pliku




angle=-3.5

for nr in range(len(M)):
    #print nr
    imm=im.fromarray(M[:,nr,:])
    M[:,nr,:]=imm.rotate(180,resample=im.BICUBIC)

for nr in range(len(M)):
    #print nr
    imm=im.fromarray(M[:,:,nr])
    M[:,:,nr]=imm.rotate(angle,resample=im.BICUBIC)




M.tofile('wspolczynnik_HR.bin')

#macierz wynikowa aktywnosci
M=np.zeros((Size_X+offset,Size_Y+offset,Size_Z+offset),dtype=Dtype)

#wpisywanie aktywnosci w komorki macierzy wynikowej M
a=A/(len(main_cyl_fill)-len(Rods)-len(Cyl_A))
for nr,i in enumerate(main_cyl_fill):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=a
#    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=0
##    if nr%1000==0:
##        print "Cylinders", float(nr)/len(main_cyl_fill)


n=0
x=0
nrr=0
for nr,i in enumerate(Cyl_A):
    if nr<N_Cyl_A[n]:
        M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=A_cyl[n]/(N_Cyl_A[n]-x)
##        if nr%1000==0:
##            print "Cylinders_A", float(nr)/len(Cyl_A)
    else:
        print (nr-nrr)
        nrr=nr
        x=N_Cyl_A[n]
        n+=1
print (nr-nrr)


for nr,i in enumerate(Rods):
    M[i[0]+offset/2,i[1]+offset/2,i[2]+offset/2]=0
##    if nr%1000==0:
##        print "Rods", float(nr)/len(Rods)

#zapisywanie wyniku do pliku

for nr in range(len(M)):
    #print nr
    imm=im.fromarray(M[:,nr,:])
    M[:,nr,:]=imm.rotate(180,resample=im.BICUBIC)

for nr in range(len(M)):
    #print nr
    imm=im.fromarray(M[:,:,nr])
    M[:,:,nr]=imm.rotate(angle,resample=im.BICUBIC)



M.tofile('aktywnosc_HR.bin')



print
print (np.sum(M))
print ("Typ danych", Dtype)
print ("Wymiary", np.shape(M), 'px')
Conc_cm3_phant=a*(Scale**3)*1000.
print ("Koncentracja w objetosci fantomu na ml", Conc_cm3_phant, "Bq/cm^3")
print ("Koncentracja na voxel", a, "Bq/vox")
print ("Rozmiar pixela", 1./Scale,"[mm]")
