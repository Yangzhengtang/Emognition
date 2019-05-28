from Crypto.Util import number


def Calculation(k1,k2,s,a,p,support_xy,support_x,N):
    s=int(s)
    a=int(a)
    p=int(p)
    support_xy=int(support_xy)
    support_x=int(support_x)
    SC_xy = number.inverse(s**(k1+k2),p)*support_xy%p//a**(k1 + k2)
    SC_x = number.inverse(s**k1,p)*support_x%p//a**k1
    if SC_x ==0:
        return SC_xy/N,0
    else:
        return SC_xy/N,SC_xy/SC_x