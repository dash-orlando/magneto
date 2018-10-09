"""
Solvers
"""

# Import Modules
import  random
import  numpy                   as      np
from    time                    import  sleep, time
from    math                    import  *
from    scipy.optimize          import  fsolve
from    scipy.optimize          import  broyden1
from    scipy.optimize          import  newton_krylov
from    scipy.optimize          import  anderson
from    scipy.optimize          import  root
from    scipy.linalg            import  norm

# Functions
def forward_lhs( const, vals ):
    K = const
    x, y, z = vals
    
    sol1 = (( K*( x**2. + y**2. + z**2. )**(-3.) *
            ( 3.*( z**2./(x**2. + y**2. + z**2.) ) + 1 )))
    
    sol2 = (( K*( (x+.05)**2. + (y-.05)**2. + z**2. )**(-3.) *
            ( 3.*( z**2./((x+.05)**2. + (y-.05)**2. + z**2.) ) + 1 )))
    
    sol3 = (( K*( (x-.05)**2. + (y-.05)**2. + z**2. )**(-3.) *
            ( 3.*( z**2./((x-.05)**2. + (y-.05)**2. + z**2.) ) + 1 )))

    print sol1, sol2, sol3
    return sol1, sol2, sol3
    

def backward_lhs( root ):
    K = const
    x, y, z = root
    sensor1 = ( K*( x**2. + y**2. + z**2. )**(-3.) *
              ( 3.*( z**2./(x**2. + y**2. + z**2.) ) + 1 ))
    
    sensor2 = ( K*( (x+.05)**2. + (y-.05)**2. + z**2. )**(-3.) *
              ( 3.*( z**2./((x+.05)**2. + (y-.05)**2. + z**2.) ) + 1 ))
    
    sensor3 = ( K*( (x-.05)**2. + (y-.05)**2. + z**2. )**(-3.) *
              ( 3.*( z**2./((x-.05)**2. + (y-.05)**2. + z**2.) ) + 1 ))
    
    return ( sensor1 - sol1, sensor2 - sol2, sensor3 - sol3)



# Evaluate normal function with an arbitrary value
const = 1.20                                                # random value of K
vals = [2.0,1.0,0.5]                                        # random positions
sol1, sol2, sol3 = forward_lhs(const, vals)                 # forward solution


# Solve function using approximate intitial guess
guess = [2.0,1.0,0.70]



# Based on the SciPy documentation, the following solvers are best for the task
#   root()

print( "SOLVING USING root():" )
solv1 = root(backward_lhs, guess, method='lm', options={'xtol':1e-20,'ftol':1e-8,'maxiter':250000})
print( solv1 ) 
print( "SOLUTION 1:" )
print( "x = %.5f || y = %.5f || z = %.5f" %(solv1.x[0], solv1.x[1], solv1.x[2]) )
solution1 = np.array((solv1.x[0], solv1.x[1], solv1.x[2]), dtype='f')
print( backward_lhs(solution1) )

print( "..." )
print( "..." )
print( "..." )


