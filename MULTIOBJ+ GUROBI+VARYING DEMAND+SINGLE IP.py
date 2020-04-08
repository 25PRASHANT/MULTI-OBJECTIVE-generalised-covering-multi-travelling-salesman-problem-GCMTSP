# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 08:30:33 2020

@author: PRASHANT
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:12:32 2020

@author: PRASHANT
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 22:27:13 2019

@author: Karnika
"""

from gurobipy import*
import os
import xlrd
from itertools import*
from scipy import spatial
from sklearn.metrics.pairwise import euclidean_distances
import math
from itertools import*
import xlsxwriter


facility_cordinate={}
cust_cordinate={}
K=[1,2]
n_facility=15
n_cust=35
nc=6            ####CHANGE LINE NO 76 ALSO
book = xlrd.open_workbook(os.path.join("1.xlsx"))
sh = book.sheet_by_name("Sheet1")
i = 1
for i in range(1,n_facility+2):  
    sp3=sh.cell_value(i,0)
    sp = sh.cell_value(i,1)
    sp2 = sh.cell_value(i,2)
    sp1=(sp,sp2)
    facility_cordinate[sp3]=(sp1)
j=1
for i in range(n_facility+2,n_cust+2+n_facility):
    sp3=sh.cell_value(i,0)
    sp = sh.cell_value(i,1)
    sp2 = sh.cell_value(i,2)
    sp1=(sp,sp2)
    cust_cordinate[sp3]=sp1  
    j=j+1

def calculate_dist(x1, x2):
    eudistance = spatial.distance.euclidean(x1, x2)
    return(eudistance) 
facility_dist={}      
for i in facility_cordinate:

    for j in facility_cordinate:
        facility_dist[i,j]=calculate_dist(facility_cordinate[i],facility_cordinate[j])
        
cust_dist={}
for i in facility_cordinate:
    for j in cust_cordinate:
        cust_dist[i,j]=calculate_dist(facility_cordinate[i],cust_cordinate[j])
a_ij={}
facility=[]
for i in range(n_facility+1):
    facility.append(i)
customers=[] 
demand={}
#for i in range(n_facility+1,n_cust+n_facility+1):
#    customers.append(i)  
#    demand[i]=1
for i in range(n_facility+1,n_cust+n_facility+1):
    customers.append(i)  
    demand[i]=sh.cell_value(i+1,3)
abc={}
    

for i in range(2,n_facility+2):
    j = 3
    xyz=[]
    while True:
        try:
            
            sp = sh.cell_value(i,j)
            xyz.append(sp)
            
            j = j + 1
            
        except IndexError:
            break
    abc[i-1]=xyz



for i in customers:
    for j in facility:
        if j!=0:
            a=abc[j]
            if i in a:
                a_ij[i,j]=1
            else:
                a_ij[i,j]=0
facility_dash=facility[1:]
D=75
   
m=Model('GTSP')

X=m.addVars(facility,facility,K,vtype=GRB.BINARY,name="Xijk")
U=m.addVars(facility,vtype=GRB.CONTINUOUS,name='U')
Y=m.addVars(facility,K,vtype=GRB.BINARY,name="Yjk")
Z=m.addVars(customers,facility  ,vtype=GRB.BINARY,name="Zij")
num=2
m.modelSense=GRB.MAXIMIZE

#model.setObjectiveN(quicksum(w[k]*R[k]*3 for k in stations), 0, 1)
#model.setOjbectiveN(quicksum(cost[l]*z[l,k] for l in L for k in stations), 1, 0)

m.setObjectiveN(sum((a_ij[i,j]*Z[i,j]*demand[i]) for i in customers for j in facility if j!=0),0,1)
m.setObjectiveN(sum(-1*(facility_dist[i,j]*X[i,j,k]) for i in facility for j in facility for k in K ),1,0)

for i in facility:
    for k in K:
        m.addConstr(sum(X[i,j,k] for j in facility  if j!=i)==Y[i,k]) 
        m.addConstr(sum(X[j,i,k] for j in facility  if i!=j )==Y[i,k])

for i in customers:
    for j in facility_dash:
        if a_ij[i,j]==1:
            m.addConstr(Z[i,j]<=sum(Y[j,k] for k in K) )
                
for k in K:
    m.addConstr(sum((facility_dist[i,j]*X[i,j,k])for i in facility for j in facility if i!=j) <= D)
    
for i in customers:
    m.addConstr(sum(Z[i,j] for j in facility if j!=0 if a_ij[i,j]==1 ) <=1)
    
for i in facility_dash:
    for j in facility_dash:
        if i!=j:
            for k in K:
                m.addConstr((U[i]-U[j]+(n_facility)*X[i,j,k])<=n_facility-1)                

m.write('GTSP1.lp')
m.optimize()
time=m.Runtime
#for v in m.getVars():
#    if v.x>0.01:
#        print('%s%g'%(v.varName,v.x))
#print('Objective:',round(m.objVal,2))
#print("time taken =",time)

v = m.getVars()

nSolutions  = m.SolCount
nObjectives = m.NumObj
print('Problem has', nObjectives, 'objectives')
print('Gurobi found', nSolutions, 'solutions')
objective=[]
solutions = []
for s in range(nSolutions):
  # Set which solution we will query from now on
  m.params.SolutionNumber = s

  # Print objective value of this solution in each objective
  print('Solution', s, ':', end='')
  for o in range(nObjectives):
#    print(o)
    # Set which objective we will query
#    if m.objNVal==m.objVal:
    m.params.ObjNumber = o
    # Query the o-th objective value
    
    if o==0:
        sol=m.ObjNVal
#        print("sol =", sol)
    if o==1 and m.objVal==sol:
#        print("yes")
        objective.append( -1*m.ObjNVal)
    print(' ',m.ObjNVal, end='')
    print()
    



#n = len(x)
#for j in range(n):
#    if x[j].Xn>0.01:
#        print(x[j].VarName, x[j].Xn, end='')
#print('')

for v in m.getVars():
    if v.x>0.01:
        print('%s%g'%(v.varName,v.x))
print('demand satisfied:',round(m.objVal,2))
print("distance travelled:",min(objective))

print("time taken =",time)




  # query the full vector of the o-th solution
#solutions.append(m.getAttr('Xn',x))

