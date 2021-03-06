import numpy as np
import math 
import multiprocessing as mp
import os 
repeat=32
n = 7
size=2*n
dim = int(math.factorial(2*n)/(math.factorial(n)*math.factorial(n))) 

i = 2*n-1
j = 2*n-2
def vecgen(n): # generates all the vectors in computational basis fo S = 0 
	dim = int(math.factorial(2*n)/(math.factorial(n)*math.factorial(n)))
	T = np.zeros(dim)
	V = np.zeros((dim,2*n))
	c = 0
	for i in range(2**(2*n)):
		if bin(i).count('1')==n:
			T[c] = i
			#print(i)
			k = list(str("{0:b}".format(i)))
			for j in range(len(k)):
				V[c,-j-1] = int(k[-j-1])
				#print(i)
			c += 1
	return(descramblr(V))

def descramblr(V):
	x = np.shape(V)[0]
	y = np.shape(V)[1]
	U = np.copy(V)
	c = 0
	d = 0
	for i in range(x):
		if V[i,-1]==0:
			U[c,:]= np.copy(V[i,:])
			c+=1
		else:
			U[dim/2+d,:]= np.copy(V[i,:])
			d+=1
	return(U)

def find(a,K):
	Z = [list(K[i,:]) for i in range(len(K[:,0]))]
	#print(Z)
	return(Z.index(list(a)))

def makeham(n,V,J,c): #Genrates hamiltonian with inputs J->the interaction strengths with the nearest neighbour, h->Field at each given spin, c->dim of hilbert space. 
	H = np.zeros((c,c))  
	#print(np.shape(V))
	#print(c)
	for a in range(c):
		for i in range(2*n):
			for j in range(i+1,2*n):
				if V[a,i]==V[a,j]:
					H[a,a] =H[a,a]+ J[i,j]*0.25
				else:
					H[a,a] =H[a,a]- J[i,j]*0.25
					t = np.zeros(2*n)
					t = np.copy(V[a,:])
		  			t[i],t[j]=t[j],t[i]
		  			b = find(t,V)
#					print(a,b,i,j)
					H[a,b] =J[i,j]*0.5
	return(H)

def makehami(n,V,J,c): #Genrates hamiltonian with inputs J->the interaction strengths with the nearest neighbour, h->Field at each given spin, c->dim of hilbert space.
    D = np.zeros((c,c))
    for a in range(c/2):
        for i in range(2*n):
            j = 2*n-1
            if J[i,j]!=0:
                if V[a,i]!=V[a,j]:
                    t = np.zeros(2*n)
                    t = np.copy(V[a,:])
                    t[i],t[j]=t[j],t[i]
                    b = find(t,V)
                    D[a,b] +=J[i,j]*0.5
                    #print(J[i,j]*0.5)
    return(D+D.T)
def LoopJ(n):
        x = np.zeros((2*n,2*n))
        for i in range(2*n-1):
                x[i,(i+1)%(2*n)] = 1
        #x[2*n-1,2*n-2] = v
        x[0,2*n-1]=1
        if n==1:
                x[0,0]=0
        return(x+x.T)

def LoopJJ(n):
	x = np.zeros((2*n,2*n))
	for i in range(2*n-1):
		x[i,(i+1)%(2*n-1)] = 1
	x[0,2*n-1]=1
	#x[2*n-1,2*n-2] = v 
	if n==1: 
		x[0,0]=0
	return(x+x.T)

def genT1(E,Ei): # generates the appropriate time evo matrices T[m,n] =exp(1j*(E[i]-Ei[j]))
	x = int(np.shape(E)[0])
	y = int(np.shape(Ei)[0])
	T = np.zeros((x,y),dtype=np.complex_)
	for i in range(x):
		for j in range(y):
			T[i,j] = np.exp(1j*(E[i]-Ei[j]))
	return(T) 

def S_z(i,V,dim):
	d = np.zeros((dim,dim))
	U = np.copy(V)-0.5
	for k in range(dim):
		d[k,k]=U[k,i] 
	return(d)

def Szpow2(A,B,Te,t):#faster under the assumption all <m|Sz_i|n> are real
	
	return(np.sum((A*Te**t)*B.T))
	
def Szpow4(Sz_i,Sz_j,Te):#computes <Sz_i(t)Sz_j(0)Sz_i(t)Sz_j(0)>, Sz_i is one and Sz_j is the other spin, Te is the time evo mat, t is the time )
	
	c = np.dot((Sz_i*Te).astype(np.complex64),Sz_j.astype(np.float32))
	return(np.sum(c*c.T))

Eve = vecgen(n)

if i==j :
	s_zi   = S_z(i,Eve,dim)
	s_zj   = np.copy(s_zi)

else:
	s_zi   = S_z(i,Eve,dim)
	s_zj   = S_z(j,Eve,dim)
	s_zk   = S_z(j-1,Eve,dim)

#np.random.seed(run)
J = LoopJ(n)
C = makeham(n,Eve,J,dim)

def runprog(run):
	for ki in range(len(win)):
		np.random.seed(run)
		v = win[ki]
		h = v*np.random.randn(2*n)
		Ha=np.copy(C) + np.diag(np.dot((Eve-0.5).astype(np.float32),h.astype(np.float32)))  
		srun=str(run)
		ev= 'rep'+ srun + '_v_'+str(v)+'_size_' + str(n)  
		eva = ev + '_evals.txt' 
		eve = ev + '_evecs.txt'
		evr = ev + '_r.txt'
		evd = ev + '_e.txt'
		Ei,H = np.linalg.eigh(Ha)
		ya = np.diff(Ei)
		r = np.zeros(dim-2)
		e = np.zeros(1)
		e[0] = max(Ei)-min(Ei)
		for i in range(dim-2):
			r[i]= min(ya[i],ya[i+1])/max(ya[i],ya[i+1])
		np.savetxt(evr,r,fmt = '%10.15f',delimiter = ',')
		np.savetxt(evd,e,fmt = '%10.15f')
'''
		if i==j:
			sz_i   = np.dot(H.T,np.dot(s_zi,H))
			sz_j   = np.copy(sz_i)
			
		else:
			sz_i   = np.dot((H.T).astype(np.float32),np.dot(s_zi.astype(np.float32),H.astype(np.float32)))
			sz_j   = np.dot((H.T).astype(np.float32),np.dot(s_zj.astype(np.float32),H.astype(np.float32)))		
			sz_k   = np.dot((H.T).astype(np.float32),np.dot(s_zk.astype(np.float32),H.astype(np.float32)))		

		tu = np.logspace(-1,3.5,num=30)
		ti = np.copy(tu)#10**tu
		qszpow2_t = np.zeros((len(tu),2))
		qszpow4_t = np.zeros((len(tu),2))
		qsii = sz_i*sz_i.T
		for k in range(len(tu)):
			t = ti[k]	
			Ein = np.exp(1j*Ei*t)
		#	abd= Ein**t
			T = np.tensordot(Ein,np.conj(Ein),axes=0)
			Sz0  = np.sum(qsii*T)
			qszpow2_t[k,:] = [t,4*Sz0/dim]

			Sz2 = Szpow4(sz_i,sz_j,T)
			qszpow4_t[k,:] = [t,16*Sz2/dim]	

			
		sze2 = 'q' + ev + 'szpow2.txt'
		np.savetxt(sze2,qszpow2_t,fmt = '%10.15f',delimiter = ',')
		sze4 = 'q' + ev + 'szpow4.txt'
		np.savetxt(sze4,qszpow4_t,fmt = '%10.15f',delimiter = ',')

#		sze2 = 'b' + ev + 'szpow2.txt'
#		np.savetxt(sze2,bszpow2_t,fmt = '%10.15f',delimiter = ',')'''


	
def readprog(repeat,w): # reading the repeats
	r = np.zeros(repeat)
	e = np.zeros(repeat)
	qsz2 = np.zeros((30,2))
	qsz4 = np.zeros((30,2))
	#bsz2 = np.zeros((19,2))
	bsz4 = np.zeros((30,2))

	for k in range(repeat):	
		run = k
		srun = str(run) 
		ev= 'rep'+ srun + '_v_'+str(w)+'_size_' + str(n) 
		
		evr = ev + '_r.txt'
		evd = ev + '_e.txt'
		xa = np.loadtxt(evr)
		r[k]= np.copy(np.average(xa))
		e[k] = np.loadtxt(evd)

		#sze2 = 'q' + ev + 'szpow2.txt'
		#sze4 = 'q' + ev + 'szpow4.txt'
		#qsz2 += np.loadtxt(sze2,delimiter=',')
		#qsz4 += np.loadtxt(sze4,delimiter=',')

        print(e)
	#ev= 'rep'+ str(repeat) + '_v_'+str(w)+'_size_' + str(size) 
	#sze2 = 'q' + ev + 'szpow2'
	#sze4 = 'q' + ev + 'szpow4'	
	#sz2=qsz2/repeat
	#sz4=qsz4/repeat
	#np.savetxt(sze2,sz2,fmt = '%10.15f',delimiter = ',')
	#np.savetxt(sze4,sz4,fmt = '%10.15f',delimiter = ',')
	return(np.average(r),np.average(e),np.std(e))


we = np.logspace(np.log10(0.5),np.log10(12),num=8)
#we[0]=0.5
#we[1]= 3.5
#we[2]= 15
win= np.copy(we)#10**we
r_m = np.zeros((len(win),2))
e_m = np.zeros((len(win),2))
de_m = np.zeros((len(win),2))

#v=1

#w=1
#runprog(5)

pool=mp.Pool()
pool.map(runprog,range(repeat))
for wi in range(len(win)):
	w = win[wi]
	r_m[wi,0]=w
	e_m[wi,0]=w
	de_m[wi,0]=w
	r_m[wi,1],e_m[wi,1],de_m[wi,1]=readprog(repeat,w)

cv = "level_stat_for"+str(n)
np.savetxt(cv,r_m,fmt = '%10.15f',delimiter = ',')
cv = "energy_stat_for"+str(n)
np.savetxt(cv,e_m,fmt = '%10.15f',delimiter = ',')
cv = "dev_stat_for"+str(n)
np.savetxt(cv,de_m,fmt = '%10.15f',delimiter = ',')
print(r_m) 
print(e_m)
print(de_m)

