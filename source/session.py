Data=loadtxt("./exp/XANES_3PCA.dat")
import PCA
Dat=Data[600:1400,1:]
P=PCA.PCA(Dat)
P.red(3)
P.varimax()
P.EMiteraction()
