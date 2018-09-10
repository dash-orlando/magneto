"""
Numerical solvers:

Bisection, Secant & Newton Raphson Method (Linear & Non-Linear).

AUTHOR  : Mohammad Odeh
DATE    : Aug. 22nd, 2017
MODIFIED: Aug. 24th, 2017
"""

import  numpy           as      np
from    numpy.linalg    import  norm
from    numpy.linalg    import  inv

'''
*
* f		:	Function of interest
* f_		:	Derivative of function (if needed)
* [a, b]	:	Interval (if needed)
* TOL		:	Tolerance for convergence
* NMAX		:	Max number of iterations
*
'''


######################################################
#                   FUNCTION DEFINITIONS
######################################################

###
### LINEAR SOLVERS
###
def bisection( f, a, b, TOL=1e-5, NMAX=500 ):
    """
    INPUT : - Function
            - Lower Bound
            - Upper Bound
            - OPTIONAL: Tolerance
            - OPTIONAL: Maximum Number of Iterations

    RETURN: - Solution
            - Residual
            - # of Iterations
    """
    n=1                                 # Counter
    res = []                            # Residual
    iter_conv = []                      # Iterative convergance
    while( n <= NMAX ):
        # Determine midpoint
        p = (a+b)/2.0
        res.append( f(p) )              # Evaluate residual

        # Check for convergence
        if (abs( res[-1] ) < TOL) or ( (b-a)/2.0 < TOL ):
            # Return solution
            return (p, res, n)
        
        else:
            n = n + 1                   # Increment counter
            if (f(p)*f(a) > 0):         # Check for signs
                a = p
            else:
                b = p

    return False                        # No solution found within iteration limit

def secant( f, x0, x1, TOL=1e-5, NMAX=500 ):
    """
    INPUT : - Function
            - Initial Guess (1)
            - Initial Guess (2)
            - OPTIONAL: Tolerance
            - OPTIONAL: Maximum Number of Iterations

    RETURN: - Solution
            - Residual
            - Iterative Convergence
            - # of Iterations
    """
    n=1                                 # Counter
    res = []                            # Residual
    iter_conv = []                      # Iterative convergance
    while( n <= NMAX ):
        # Approximate value of x
        x2 = x1 - f(x1)*((x1-x0)/(f(x1)-f(x0)))
        res.append( f(x2) )             # Evaluate residual
        iter_conv.append( (x2 - x1) )   # Evaluate iterative convergance
        
        # If within tolerance, stop
        if (abs( iter_conv[-1] ) < TOL) and (abs(res[-1]) < TOL):
            # Return solution
            return (x2, res, iter_conv, n)

        # Else Update guesses and iterate onto the next point
        else:
            x0 = x1
            x1 = x2
            n = n + 1                   # Increment counter

    return False                        # No solution found within iteration limit

def NR( f, f_, x0, TOL=1e-5, NMAX=100 ):
    """
    INPUT : - Function
            - Derivative of Function
            - Initial Guess
            - OPTIONAL: Tolerance
            - OPTIONAL: Maximum Number of Iterations

    RETURN: - Solution
            - Residual
            - Iterative Convergence
            - # of Iterations
    """
    n=1                                 # Counter
    res = []                            # Residual
    iter_conv = []                      # Iterative convergance

    while( n <= NMAX ):
        # Approximate value of x
        x1 = x0 - (f(x0)/f_(x0))
        res.append( f(x1) )             # Evaluate residual
        iter_conv.append( (x1-x0) )     # Evaluate iterative convergence
        if (abs(iter_conv[-1]) < TOL):
            # Return solution
            return (x1, res, iter_conv, n)
        
        else:
            x0 = x1                     # Update solution/guess
            n = n + 1                   # Increment counter

    return (False, res, iter_conv, n)   # No solution found within iteration limit

###
### NON-LINEAR SOLVERS
###
# Newton Raphson for a system of non-linear equations
def NR_NL( x0, TOL=1e-5, NMAX=100 ):
    """
    INPUT : - np.array[Initial Guess]
            - OPTIONAL: Tolerance
            - OPTIONAL: Maximum Number of Iterations

    RETURN: - np.array[Solution]
            - Residual
            - Iterative Convergence
            - # of Iterations
    """
    n=0                                 # Counter
    res = []                            # Residual
    iter_conv = []                      # Iterative convergance
    N = len(x0)                         # Get vector length for matrix construction
    J = np.empty((N,N), dtype='float64')# Construct matrix of size  (NxN)
    b = np.empty((N,1), dtype='float64')# Construct array of size   (Nx1)

    # Start iterating
    while( n <= NMAX ):
        # Construct Jacobian
        for i in range( N ):
            for j in range( N ):
                J[i, j] = jacobian(i, j, x0)
            b[i] = -func(i, x0)         # Evaluate function

        z = inv(J).dot(b)               # Calculate Z Array
        x0 = x0 + z                     # Update solution
        res.append( norm(b) )           # Evaluate residual
        iter_conv.append( norm(z) )     # Evaluate iterative convergence

        if (abs(res[-1]) < TOL) and (iter_conv[-1] < TOL):
            # Return solution
            return (x0, res, iter_conv, n)

        else:
            n = n + 1                   # Increment counter

    return(False, res, iter_conv, n)    # No solution found within iteration limit

# Levenberg-Marquardt
def LM( x0, TOL=1e-5, NMAX=100 ):
    """
    INPUT : - np.array[Initial Guess]
            - OPTIONAL: Tolerance
            - OPTIONAL: Maximum Number of Iterations

    RETURN: - np.array[Solution]
            - Residual
            - Iterative Convergence
            - # of Iterations
    """
    n=0                                     # Counter
    res = []                                # Residual
    iter_conv = []                          # Iterative convergance
    N = len(x0)                             # Get vector length for matrix construction
    J = np.empty((N,N), dtype='float64')    # Construct matrix of size  (NxN)
    b = np.empty((N,1), dtype='float64')    # Construct array of size   (Nx1)
    I = np.identity(N, dtype='float64')     # Construct identity matrix (NxN)
    Y = float(1e8)

    # Start iterating
    while( n <= NMAX ):
        # Construct Jacobian
        for i in range( N ):
            for j in range( N ):
                J[i, j] = jacobian(i, j, x0)# Evaluate Jacobian
            b[i] = func(i, x0)              # Evaluate function

        x_old = x0
        H = inv(np.transpose(J).dot(J)+Y*I).dot(np.transpose(J))
        x0 = x0 - H.dot(b)                  # Update solution
        res.append( norm(b) )               # Evaluate residual
        iter_conv.append( norm(x0-x_old) )  # Evaluate iterative convergence

        if (abs(res[-1]) < TOL) and (iter_conv[-1] < TOL):
            # Return solution
            return (x0, res, iter_conv, n)

        else:
            n = n + 1                       # Increment counter
            Y = Y*0.01

    return(False, res, iter_conv, n)        # No solution found within iteration limit

######################################################
#               AUXILLIARY FUNCTIONS
######################################################
def func(i, x0):
    #x, y = x0
    k  = 15
    a  = 0.5
    T0 = 150
    T1 = x0[0]
    T2 = x0[1]
    T3 = x0[2]
    T4 = x0[3]
    TL = 25
    if( i == 0 ):
        #f = cos(x) - y
        f = (k+a/2*(T1+T0))*T0-(2*k+a/2*(T0+2*T1+T2))*T1+(k+a/2*(T1+T2))*T2
        return ( f )
    
    elif( i == 1):
        #f = x - sin(y)
        f = (k+a/2*(T2+T1))*T1-(2*k+a/2*(T1+2*T2+T3))*T2+(k+a/2*(T2+T3))*T3
        return ( f )
    
    elif( i == 2):
        f = (k+a/2*(T3+T2))*T2-(2*k+a/2*(T2+2*T3+T4))*T3+(k+a/2*(T3+T4))*T4
        return ( f )

    elif( i == 3):
        f = (k+a/2*(T4+T3))*T3-(2*k+a/2*(T3+2*T4+TL))*T4+(k+a/2*(T4+TL))*TL
        return ( f )
    
    else:
        raise Exception

# Approximate derivative using either FFD, BFD, or CFD
def df_approx( f, x0, dx=1e-5, METHOD='FFD' ):
    """
    INPUT : - Function
            - Point of Interest
            - OPTIONAL: Tolerance
            - OPTIONAL: FD Method

    RETURN: - Derivative at Point
    """
    a = x0                      # Create a copy
    # Estimate derivative using FFD
    if (METHOD == 'FFD'):
        a = x0 + dx             # Add the finite difference
        df = (f(a) - f(x0))/(dx)

    # Estimate derivative using BFD
    elif (METHOD == 'BFD'):
        a = a - dx              # Subtract the finite difference
        df = (f(x0) - f(a))/(dx)

    # Estimate derivative using CFD
    elif (METHOD == 'CFD'):
        a = x0 + dx             # Add the finite difference
        pstv = f(a)             # Evaluate function
        a = x0 - dx             # Subtract the finite difference
        ngtv = f(a)             # Evaluate function
        df = (pstv-ngtv)/(2*dx)  # Approximate derivative


    # Invalid method specified
    else:
        print( "INVALID OPTION: %r" %METHOD)
        return False

    # Return answer
    return ( df )

# Build the Jacobian matrix
def jacobian( i, j, x0, dx=1e-5 ):
    """
    INPUT : - Row
            - Column
            - Point of Interest
            - OPTIONAL: Tolerance

    RETURN: - Partial Derivative at Point
    """
    x = []
    for k in range(len(x0)):
        x.append(x0.item(k))    # Extract elements from array and put in list 'cause Python!
    a = x[:]                    # Create a local copy of the initial guess
    a[j] = a[j] + dx            # Add the finite difference to the corresponding variable

    # Estimate derivative
    df = (func(i, (a)) - func(i, (x)))/(dx)

    # Return answer
    return ( df )                           


######################################################
#                   SETUP PROGRAM
######################################################
def f(x):
    """
    Function x^3 - x -2
    Example function.
    """
    return x**3. - x - 2

def f_(x):
    """
    Derivate of the function f(x) = x^3 - x - 2
    Needed for Newton-Raphson.
    """
    return 3*x**2 - 1


######################################################
#                   START PROGRAM
######################################################
if __name__ == "__main__":

    # Invoking Bisection Method
    print( "Bisection Method" )
    sln, res, n = bisection(f, 1, 2)
    print( "SOLUTION: %3.5f || Iterations: %3.5f" %(sln, n) )
    print( "Residual:- " )
    for i in range( len(res) ):
        print( "%2i: %8.5f" %(i, res[i]) )
        if ( i == len(res) - 1):
            print('')

    # Invoking Secant Method
    print( "Secant Method" )
    sln, res, conv, n = secant(f, 1, 2)
    print( "SOLUTION: %3.5f || Iterations: %3.5f" %(sln, n) )
    print( "   Residual\t  ||   Convergence" )
    for i in range( len(res) ):
        print( "%2i: %8.5f\t  ||\t%8.5f" %(i, res[i], conv[i]) )
        if ( i == len(res) - 1):
            print('')

    #Invoking Newton Raphson Method
    print( "Newton-Raphson Method" )
    sln, res, conv, n = NR(f, f_, 1)
    print( "SOLUTION: %3.5f || Iterations: %3.5f" %(sln, n) )
    print( "   Residual\t  ||   Convergence" )
    for i in range( len(res) ):
        print( "%2i: %8.5f\t  ||\t%8.5f" %(i, res[i], conv[i]) )
        if ( i == len(res) - 1):
            print('')

    # Invoking Newton-Raphson for nonlinear system
    x0 = np.array(([100], [100], [100], [100]), dtype='float64')
    print( "Newton-Raphson Method - NON-LINEAR" )
    sln, res, conv, n = NR_NL(x0, TOL=1e-10)
    print( "SOLUTION:" )
    print(sln)
    print( "Iterations: %3.3f" %( n) )
    print( "   Residual\t  ||   Convergence" )
    for i in range( len(res) ):
        print( "%2i: %1.2e\t  ||\t%1.2e" %(i, res[i], conv[i]) )
        if ( i == len(res) - 1):
            print('')

    # Invoking Levenberg-Marquardt
    x0 = np.array(([100], [100], [100], [100]), dtype='float64')
    print( "Levenberg-Marquardt Method" )
    sln, res, conv, n = LM(x0, TOL=1e-10)
    print( "SOLUTION:" )
    print(sln)
    print( "Iterations: %3.3f" %( n) )
    print( "   Residual\t  ||   Convergence" )
    for i in range( len(res) ):
        print( "%2i: %1.2e\t  ||\t%1.2e" %(i, res[i], conv[i]) )
        if ( i == len(res) - 1):
            print('')

"""
References
1 - http://kestrel.nmt.edu/~raymond/software/python_notes/paper003.html
"""
