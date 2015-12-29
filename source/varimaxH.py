# Varimax4M - Varimax rotation as described by Harman (1967, pp. 304-308)
#             and implemented by BMDP-4M (Dixon, 1992, pp. 602-603),
#             using the simplicity criterion G instead of Vmax
#
# Usage: [Y, G] = Varimax4M ( X, maxit, tol, norm)
#
#    Only arguments X and Y requested.
#
# Input arguments:
#        X = variables-by-factors loadings matrix
#    maxit = maximum number of iterations
#            (default = 100)
#      tol = convergence criterion threshold for rotation
#            (default = 1e-4)
#     norm = perform Kaiser's normalization
#            (default = 1 = normalize)
#
# Output arguments:
#        Y = Varimax-rotated variables-by-factors loadings matrix
#        G = simplicity criterion for each iteration (Dixon, 1992)
#        V = Varimax criterion for each iteration (Harman, 1967)
#            (computations for V are only listed in comments)
#
# Terminology following Harman (1967), Dixon (1992), and Park (2003)
#    p = number of variables (rows)
#    m = number of factors (columns)
#    X = initial p-by-m matrix
#    Y = rotated p-by-m matrix
#    h = communalities of the variables (rows)
# 
# References
# ----------
#    Dixon WJ (Ed.) (1992). BMDP Statistical Software Manual: To 
#       Accompany the 7.0 Software Release. University of California 
#       Press, Berkeley, CA.
#    Harman HH (1967). Modern Factor Analysis (2nd ed). University of 
#       Chicago Press, Chicago.
#    Park T (March 2003). A note on terse coding of Kaiser's Varimax 
#       rotation using complex number representation. (http://www.orie.
#       cornell.edu/~trevor/Research/vnote.pdf)
#
# Copyright (C) 2003 by Jurgen Kayser (Email: kayserj@pi.cpmc.columbia.edu)
# GNU General Public License (http://www.gnu.org/licenses/gpl.txt)
# Updated: $Date: 2003/06/27 07:05:00 $ $Author: jk $
#

import numpy as np
import numpy.linalg as linalg



def SimplicityG(Y):
    g = 0;  
    row,column=Y.shape
    for i in range(column):
      for j  in range(column): 
        if (i != j):   
            g += sum((Y[:,i]**2)*(Y[:,j]**2))-   \
                    (  (1/row) *  ( sum(Y[:,i]**2)* sum(Y[:,j]**2)  )) 
    return g


def varimax(x, normalize=True,  tol=1e-10, maxit=1000):    #positive=True,
    if len(x.shape)!=2:
        raise ValueError, 'AMAT must be 2-dimensional'
    elif len(x.shape)==2:     
        row, column = x.shape
        if normalize:
            rl = np.tile(np.sqrt(np.diag(np.dot(x,x.T))), (column,1)).T#; % By rows.l = repmat( sqrt(diag( x*x' )), [1,nc] ); % By rows.
            Y = x/rl
        else: Y=x    


       
    g = SimplicityG(Y)



    it = 0;
    G = [[it, g, tol]];
    G_old = g     # previous simplicity criterion
    YY = Y        # rotated matrix at begin of current iteration
    #V = [it, (row * sum(sum(Y**4)) - sum(sum(Y**2)**2))];

    for it in range(maxit):
        for i in range(column-1):
            for j in range(i+1,column):
                # Determine optimal angle phi to rotate columns i,j (Harman, 1967, p. 307)
                #       x = Y(:,i); y = Y(:,j); u = x.^2 - y.^2; v = 2 * x .* y;
                #       w = u.^2 - v.^2; A = sum(u), B = sum(v);C = sum(w);D = 2 * sum(u .* v);
                #       fn = D - 2 * (A * B) / p;fd = C - (A^2 - B^2) / p;t = atan2(fn,fd)/4;
                # The above computations result in exactly the same t value if replaced
                # by the the following terse code statement, which computes the rotation
                # angle phi as the angle in the complex plane (Park, 2003):
                t = np.angle(sum((Y[:,i]+1j*Y[:,j])**4)/row - (sum((Y[:,i]+1j*Y[:,j])**2)/row)**2)/4
                # rotate the two vectors ... M(n,2)*(2,2)  =Z(n,2)
                R=np.array([[np.cos(t), -np.sin(t)],[np.sin(t),np.cos(t)]])
                XY = np.dot(np.column_stack((Y[:,i],Y[:,j])),R)
                # ... and replace the two columns in the matrix
                Y[:,i] = XY[:,0]
                Y[:,j] = XY[:,1]
                pass   
            pass
        pass



        # compute rotation criterion for this iteration
        g = SimplicityG(Y);

        if abs(G_old - g)<tol:
            print "\nvarimax converged at iteration n.", it,"\n"
            if G_old<g:           # if the previous solution was better
                 Y = YY;           #% report the previous one
            else:                  
                 G.append([it, g, (G_old - g)])
            break
        pass
    
                   
  
        YY = Y
        G.append([it, g, (G_old - g)])
        G_old = g
    pass

    
    if normalize:
       YY = Y*rl             # reverse Kaiser's normalization
    Rot=np.dot(x.T,YY)
    return YY, Rot  
