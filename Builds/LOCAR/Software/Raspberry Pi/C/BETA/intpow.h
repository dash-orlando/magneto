/*
 * Compute exponents
 * 
 * Reference:-
 * 		https://stackoverflow.com/questions/213042/how-do-you-do-exponentiation-in-c
 */

// a: base
// b: exponent
double intpow(double a, int b)
{
  double r = 1.0;
  if (b < 0)
  {
    a = 1.0 / a;
    b = -b;
  }
  while (b)
  {
    if (b & 1)
      r *= a;
    a *= a;
    b >>= 1;
  }
  return r;
}
