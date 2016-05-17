import re
from xtables import atomic_weigh as at_w

atom_p= re.compile('([A-Z][a-z]?)(\d*\.?\d*)')
braket_p= re.compile('(\([\w.]*\))(\d*\.?\d*)')
mul =lambda x,y: str(float(x)*float(y)) if (x and y) else x or y 
addi =lambda x,y: str(float(x)+float(y)) if (x and y) else str(float(x or y or "1")+1)
longjoin =lambda x,y:"".join(["".join((item[0],mul(item[1],y))) for item in x]) 


            
 
            




class c_formula():
    def __init__(self, Formula): 
        self.start_formula= Formula    
        self.__bruteformula__()
        self.__WP_c__()
    
    def __bruteformula__(self):
        stringa=self.start_formula
        def inbraket(grb): 
            s1=re.findall(atom_p , grb.group(0))
            return longjoin(s1,grb.group(2))     
        while True:
            if stringa.find(")")>-1:
                stringa=re.sub(braket_p,inbraket, stringa)
            else:
                form=re.findall(atom_p , stringa)
                form.sort()
                form[0]=list(form[0])
                for i in  range(1,len(form)):
                    form[i]=list(form[i])
                    if form[i][0]==form[i-1][0]:
                        form[i-1][1]=addi(form[i-1][1],form[i][1]) 
                        form.pop(i)
                self.formula={}
                for i,j in form: self.formula[i]=float(j) if j else 1. 
                self.brute=longjoin(form,"")
                return
                
    def __MW_c__(self):
        self.MW=0
        for i,j in re.findall(atom_p , self.brute):
            self.MW+=at_w[i]*float(j) if j else at_w[i] 
            
    def __WP_c__(self):
        if not(hasattr(self, "MW")):
            self.__MW_c__()
            self.WP={}    
        for i,j in re.findall(atom_p , self.brute):
            self.WP[i]=at_w[i]*float(j)/self.MW if j else at_w[i]/self.MW
    def Omol_c(self,grammi):
        self.Omol=(grammi/self.MW)*self.formula["O"]
        print Omol
            
            
            
def exchange(mol1,x1,mol2,x2):
    return (mol1*x1+mol2*x2)/(mol1+mol2)
    
    
    
if __name__ == "__main__":
    formula = raw_input("\n\nWrite formula  \n")
    sample=c_formula(formula)
    formula2=raw_input("which information \nM =molecular weigh\nW= weigh percent\nB= bruteformula\
                        \nIt is possible more letter example (BWM)")
    if formula2=="":formula2="BMW"                    
    for i in formula2:
        if i == "M": print  "\nMolecular weight:\n ",sample.MW," uma" 
        elif i =="B": print  "\nbrute formula:\n ",sample.brute
        elif i== "W":
            print "\nWeight percent"
            for j in  sample.WP:
                print j," = ",round(sample.WP[j],6)*100, " %"
        pass    
            
        
                  
                  

