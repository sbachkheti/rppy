#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   rppy - a geophysical library for Python
#   Copyright (c) 2014, Sean M. Contenti
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#   TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import numpy as np


def shuey(vp1, vs1, rho1, vp2, vs2, rho2, theta1):
    """
    Calculate the AVO response for a PP reflection based on the Shuey
    (three-term) approximation to the Zoeppritz equations.

    :param vp1: Compressional velocity of upper layer.
    :param vs1: Shear velocity of upper layer.
    :param rho1: Density of upper layer.
    :param vp2: Compressional velocity of lower layer.
    :param vs2: Shear velocity of lower layer.
    :param rho2: Density of lower layer.
    :param theta1: Angle of incidence for P wave in upper layer.
    """
    theta2, thetas1, thetas2, p = snell(vp1, vp2, vs1, vs2, theta1)
    dvp = vp2 - vp1
    drho = rho2 - rho1
    dvs = vs2 - vs1
    rho = (rho1 + rho2) / 2.
    vs = (vs1 + vs2) / 2.
    vp = (vp1 + vp2) / 2.
    theta = (theta1 + theta2)/2

    A = 0.5*(dvp/vp + drho/rho)
    B = 0.5*dvp/vp - 2*vs**2/vp**2*(drho/rho + 2*dvs/vs)
    C = 0.5*dvp/vp

    Rpp = A + B*np.sin(theta)**2 + C*(np.tan(theta)**2 - np.sin(theta)**2)

    return(Rpp)


def aki_richards(vp1, vs1, rho1, vp2, vs2, rho2, theta1):
    """
    Calculate the AVO response for a PP reflection based on the Aki-Richards
    approximation to the Zoeppritz equations.

    :param vp1: Compressional velocity of upper layer.
    :param vs1: Shear velocity of upper layer.
    :param rho1: Density of upper layer.
    :param vp2: Compressional velocity of lower layer.
    :param vs2: Shear velocity of lower layer.
    :param rho2: Density of lower layer.
    :param theta1: Angle of incidence for P wave in upper layer.
    """
    theta2, thetas1, thetas2, p = snell(vp1, vp2, vs1, vs2, theta1)
    dvp = vp2 - vp1
    dvs = vs2 - vs1
    drho = rho2 - rho1
    theta = (theta1 + theta2) / 2.
    rho = (rho1 + rho2) / 2.
    vp = (vp1 + vp2) / 2.
    vs = (vs1 + vs2) / 2.

    Rpp = (0.5 * (1 - 4 * p**2 * vs**2) * (drho / rho) +
           (dvp / (2 * np.cos(theta)**2 * vp)) - (4 * p**2 * vs**2 * dvs / vs))

    return(Rpp)


def zoeppritz(vp1, vs1, rho1, vp2, vs2, rho2, theta1):
    """
    Calculate the AVO response for a PP reflection based on the exact matrix
    formulation of the Zoeppritz equations.

    :param vp1: Compressional velocity of upper layer.
    :param vs1: Shear velocity of upper layer.
    :param rho1: Density of upper layer.
    :param vp2: Compressional velocity of lower layer.
    :param vs2: Shear velocity of lower layer.
    :param rho2: Density of lower layer.
    :param theta1: Angle of incidence for P wave in upper layer.
    """
    # Need reflection and refraction angles for Zoeppritz
    theta2, thetas1, thetas2, p = snell(vp1, vp2, vs1, vs2, theta1)

    Rpp = np.zeros(np.shape(theta1))
    Rps = np.zeros(np.shape(theta1))
    Tpp = np.zeros(np.shape(theta1))
    Tps = np.zeros(np.shape(theta1))

    for n in np.arange(0, len(theta1)):

        M = np.array([
            [-np.sin(theta1[n]), -np.cos(thetas1[n]),
             np.sin(theta2[n]), np.cos(thetas2[n])],
            [np.cos(theta1[n]), -np.sin(thetas1[n]),
             np.cos(theta2[n]), -np.sin(thetas2[n])],
            [2.*rho1*vs1*np.sin(thetas1[n])*np.cos(theta1[n]),
             rho2*vs1*(1.-2.*np.sin(thetas2[n])**2),
             2.*rho2*vs2*np.sin(thetas2[n])*np.cos(theta2[n]),
             rho2*vs2*(1.-2.*np.sin(thetas2[n])**2)],
            [-rho1*vp1*(1.-2.*np.sin(thetas1[n])**2),
             rho1*vs1*np.sin(2.*thetas1[n]),
             rho2*vp2*(1.-2.*np.sin(thetas2[n])**2),
             -rho2*vs2*np.sin(2.*thetas2[n])]])

        N = np.array([
            [np.sin(theta1[n]), np.cos(thetas1[n]),
             -np.sin(theta2[n]), -np.cos(thetas2[n])],
            [np.cos(theta1[n]), -np.sin(thetas1[n]),
             np.cos(theta2[n]), -np.sin(thetas2[n])],
            [2.*rho1*vs1*np.sin(thetas1[n])*np.cos(theta1[n]),
             rho2*vs1*(1.-2.*np.sin(thetas2[n])**2),
             2.*rho2*vs2*np.sin(thetas2[n])*np.cos(theta2[n]),
             rho2*vs2*(1.-2.*np.sin(thetas2[n])**2)],
            [rho1*vp1*(1.-2.*np.sin(thetas1[n])**2),
             -rho1*vs1*np.sin(2.*thetas1[n]),
             -rho2*vp2*(1.-2.*np.sin(thetas2[n])**2),
             rho2*vs2*np.sin(2.*thetas2[n])]])

        Z = np.dot(np.linalg.inv(M), N)

        Rpp[n] = Z[0][0]
        Rps[n] = Z[1][0]
        Tpp[n] = Z[2][0]
        Tps[n] = Z[3][0]

    return(Rpp)


def bortfeld(vp1, vs1, rho1, vp2, vs2, rho2, theta1):
    """
    Calculate the AVO response for a PP reflection based on the Bortfeld
    approximation to the Zoeppritz equations.

    :param vp1: Compressional velocity of upper layer.
    :param vs1: Shear velocity of upper layer.
    :param rho1: Density of upper layer.
    :param vp2: Compressional velocity of lower layer.
    :param vs2: Shear velocity of lower layer.
    :param rho2: Density of lower layer.
    :param theta1: Angle of incidence for P wave in upper layer.
    """
    theta2, thetas1, thetas2, p = snell(vp1, vp2, vs1, vs2, theta1)

    Rpp = (0.5 * np.log((vp2 * rho2 * np.cos(theta1)) /
           (vp1 * rho1 * np.cos(theta2))) + (np.sin(theta1)/vp1)**2 * (vs1**2 -
           vs2**2) * (2 + np.log(rho2 / rho1) / np.log(vs2 / vs1)))

    return Rpp


def snell(vp1, vp2, vs1, vs2, theta1):
    """
    Calculates the angles of and refraction and reflection for an incident
    P-wave in a two-layered system.

    :param vp1: Compressional velocity of upper layer.
    :param vp2: Compressional velocity of lower layer.
    :param vs1: Shear velocity of upper layer.
    :param vs2: Shear velocity of lower layer.
    :param theta1: Angle of incidence of P-wave in upper layer
    """
    theta_crit_1 = np.arcsin(vp1/vp2)
    theta_crit_2 = np.arcsin(vp1/vs2)

    p = np.full(np.shape(theta1), None)
    theta2 = np.full(np.shape(theta1), None)
    thetas1 = np.full(np.shape(theta1), None)
    thetas2 = np.full(np.shape(theta1), None)

    for n in np.arange(0, len(theta1)):
        p[n] = np.sin(theta1[n])/vp1        # Ray parameter
        thetas1[n] = np.arcsin(p[n]*vs1)    # S-wave reflection

        if theta1[n] >= theta_crit_1:
            theta2[n] = None
            thetas2[n] = np.arcsin(p[n]*vs2)    # S-wave refraction
        elif theta1[n] >= theta_crit_2:
            theta2[n] = None
            thetas2[n] = None                   # S-wave refraction
        else:
            theta2[n] = np.arcsin(p[n]*vp2)     # P-wave refraction
            thetas2[n] = np.arcsin(p[n]*vs2)    # S-wave refraction

    return(theta2, thetas1, thetas2, p)


def thomsen(C):
    """
    Returns the Thomsen parameters that characterise transversely isotropic
    materials, computed from the components of the elastic stiffness matrix C.
    """

    e = (C[0][0] - C[2][2]) / (2*C[2][2])
    y = (C[5][5] - C[4][4]) / (2*C[4][4])
    d = ((C[0][2] + 2*C[4][4] - C[2][2])*(C[0][2] + C[2][2]) /
         (2*C[2][2]*(C[2][2] - C[4][4])))
    dv = (((C[0][2] + C[4][4])**2 - (C[2][2] - C[4][4])**2) /
          (2*C[2][2]*(C[2][2] - C[4][4])))

    return(e, d, y, dv)


def Cij(e, d, y, p, Vp, Vs):
    """
    Returns the elastic stiffness elements C11, C33, C13, C55, and C66 that
    characterize transversely isotropic materials, using the Thomsen parameters
    and elastic parameters.
    """
    C = np.zeros(shape=(6, 6))
    f = 1 - (Vs/Vp)**2
    dtil = f*(np.sqrt(1 + 2*d/f) - 1)

    C[0][0] = p*Vp**2*(1 + 2*e)
    C[1][1] = C[0][0]
    C[2][2] = p*Vp**2
    C[3][3] = p*Vp**2*(1 - f)
    C[4][4] = C[3][3]
    C[5][5] = p*Vp**2*(1 - f)*(1 + 2*y)
    C[0][2] = p*Vp**2*(2*f + dtil - 1)
    C[2][0] = C[0][2]
    C[0][1] = C[0][0] - 2*C[5][5]
    C[1][0] = C[0][1]

    return(C)


def ruger_vti(Vp1, Vs1, p1, e1, d1,
              Vp2, Vs2, p2, e2, d2, theta1):
    """
    Computes the reflectivity response for a weakly anisotripic material with
    vertically transverse isotropy using the equations of Thomsen (1992) and
    Ruger (1997).
    """
    theta2, thetas1, thetas2, p = snell(Vp1, Vp2, Vs1, Vs2, theta1)
    theta = (theta1 + theta2)/2
    theta = theta1

    u1 = p1*Vs1**2
    u2 = p2*Vs2**2
    Z1 = p1*Vp1
    Z2 = p2*Vp2

    a = (Vp1 + Vp2)/2
    B = (Vs1 + Vs2)/2
    Z = (Z1 + Z2)/2
    u = (u1 + u2)/2

    dZ = Z2 - Z1
    da = Vp2 - Vp1
    du = u2 - u1
    dd = d2 - d1
    de = e2 - e1

    Rpp_iso = ((1/2)*(dZ/Z) +
               (1/2)*(da/a - (2*B/a)**2*(du/u))*np.sin(theta)**2 +
               (1/2)*(da/a)*np.sin(theta)**2*np.tan(theta)**2)

    Rpp_an = (dd/2)*np.sin(theta)**2 + (de/2)*np.sin(theta)**2*np.tan(theta)**2

    Rpp = Rpp_iso + Rpp_an

    return(Rpp)


def exact_vti(V1, V2, V3, V4, p1, p2, theta1,
              C1_11, C1_13, C1_33, C1_55,
              C2_11, C2_13, C2_33, C2_55):
    """
    Returns the exact reflectivity coefficients for a VTI medium computed using
    the relations of Daley and Hron (1977).

    :param V1: P-velocity of upper medium.
    :param V2: P-velocity of lower medium.
    :param V3: S-velocity of upper medium.
    :param V4: S-velocity of lower medium.
    :param p1: Density of upper medium.
    :param p2: Density of lower medium.
    :param theta1: Incidence angle of incident P-wave in upper medium.
    """

    # TODO: There's gotta be a better way to implement these equation than
    #       transcribing them from the 1977 paper. This is insane.
    theta2, theta3, theta4, p = snell(V1, V2, V3, V4, theta1)

    x = np.sin(theta1)
    n = V1/V2
    k1 = V3/V1
    k2 = V4/V2

    P = np.sqrt(1 - x**2)
    Q = np.sqrt(1 - k1**2*x**2)
    S = np.sqrt(1 - x**2/n**2)
    R = np.sqrt(1 - k2**2*x**2/n**2)

    # Upper medium parameters
    A1_11 = C1_11 / p1
    A1_33 = C1_33 / p1
    A1_55 = C1_55 / p1
    A1_13 = C1_13 / p1

    A1_1 = 2*(A1_13 + A1_55)**2 - (A1_33 - A1_55)*(A1_11 + A1_33 - 2*A1_55)
    A1_2 = (A1_11 + A1_33 - 2*A1_55)**2 - 4*(A1_13 + A1_55)**2
    Q1 = np.sqrt((A1_33 - A1_55)**2 +
                 2*A1_1*np.sin(theta1) +
                 A1_2*np.sin(theta1))
    l1 = np.sqrt(((Q1 - A1_33 + A1_55)/np.sin(theta1)**2 +
                 (A1_11 + A1_33 - 2*A1_55))/(2*Q1))
    m1 = np.sqrt(((Q1 - A1_11 + A1_55)/np.cos(theta1)**2 +
                 (A1_11 + A1_33 - 2*A1_55))/(2*Q1))
    l3 = np.sqrt(((Q1 - A1_33 + A1_55)/np.sin(theta3)**2 +
                 (A1_11 + A1_33 - 2*A1_55))/(2*Q1))
    m3 = np.sqrt(((Q1 - A1_11 + A1_55)/np.cos(theta3)**2 +
                 (A1_11 + A1_33 - 2*A1_55))/(2*Q1))

    d1 = l3*C1_33 - m3*C1_13
    e1 = l1*C1_13 + (m1*C1_33 - l1*C1_13)*np.cos(theta1)**2
    w1 = V1/V3*(1/(l1+m1))*(m3*np.cos(theta3)**2 - l3*np.sin(theta3)**2)
    B1 = C1_55

    # Lower medium parameters
    A2_11 = C2_11 / p2
    A2_33 = C2_33 / p2
    A2_55 = C2_55 / p2
    A2_55 = C2_55 / p2
    A2_13 = C2_13 / p2

    A2_1 = 2*(A2_13 + A2_55)**2 - (A2_33 - A2_55)*(A2_11 + A2_33 - 2*A2_55)
    A2_2 = (A2_11 + A2_33 - 2*A2_55)**2 - 4*(A2_13 + A2_55)**2
    Q2 = np.sqrt((A2_33 - A2_55)**2 +
                 2*A2_1*np.sin(theta2) +
                 A2_2*np.sin(theta2))
    l2 = np.sqrt(((Q2 - A2_33 + A2_55)/np.sin(theta2)**2 +
                 (A2_11 + A2_33 - 2*A2_55))/(2*Q2))
    m2 = np.sqrt(((Q2 - A2_11 + A2_55)/np.cos(theta2)**2 +
                 (A2_11 + A2_33 - 2*A2_55))/(2*Q2))
    l4 = np.sqrt(((Q2 - A2_33 + A2_55)/np.sin(theta4)**2 +
                 (A2_11 + A2_33 - 2*A2_55))/(2*Q2))
    m4 = np.sqrt(((Q2 - A2_11 + A2_55)/np.cos(theta4)**2 +
                 (A2_11 + A2_33 - 2*A2_55))/(2*Q2))

    d2 = l4*C2_33 - m4*C2_13
    e2 = V1/V2*(l2*C2_13 + (m2*C2_33 - l2*C2_13)*np.cos(theta2)**2)
    w2 = V1/V4*(1/(l1+m1))*(m4*np.cos(theta4)**2 - l4*np.sin(theta4)**2)
    B2 = C2_55

    l = (l2+m2)/(l1+m1)

    T1 = e2 - (e1*l2)/(n*l1)
    T2 = B2*w2*k1*l3/m1 - B1*(w1*k2*l4)/(n*m1)
    T3 = B2*w2 + B1*(k2*x**2*l4)/(n*m1)
    T4 = e2*m3/l1 + (d1*x**2*l2)/(n*l1)
    T5 = B1*(w1 + k1*x**2*l3/m1)
    T6 = e2*m4/l1 + (d2*x**2*l2)/(n*l1)
    T7 = B2*l - B1*m2/m1
    T8 = d2*m3/l1 - d1*m4/l1
    T9 = B2*(w2*m2/m1 + k2*x**2*l*l4/(n*m1))
    T10 = e1*m3/l1 + d1*x**2
    T11 = e1*m4/l1 + d2*x**2
    T12 = B2*k1*x**2*l*l3/m1 + B1*w1*m2/m1

    E1 = T1*T2*x**2
    E2 = T3*T4*P*Q
    E3 = T5*T6*P*R
    E4 = T7*T8*x**2*P*Q*R*S
    E5 = T9*T10*Q*S
    E6 = T11*T12*R*S
    D = E1 + E2 + E3 + E4 + E5 + E6

    Rpp = (-E1 + E2 + E3 + E4 - E5 - E6)/D

    return(Rpp)


def ruger_hti(Vp1, Vs1, p1, e1, dv1, y1,
              Vp2, Vs2, p2, e2, dv2, y2,
              theta1, az):
    """
    Calculate P-wave reflection coefficient (Rpp) as a function of incidence
    angle and azimuth for an anisotropic material with horizontal transverse
    isotropy using the Ruger [1996] approximation.
    """
    theta2, thetas1, thetas2, p = snell(Vp1, Vp2, Vs1, Vs2, theta1)
    u1 = p1*Vs1**2
    u2 = p2*Vs2**2
    Z1 = p1*Vp1
    Z2 = p2*Vp2

    a = (Vp1 + Vp2)/2
    B = (Vs1 + Vs2)/2
    Z = (Z1 + Z2)/2
    u = (u1 + u2)/2

    dZ = Z2 - Z1
    da = Vp2 - Vp1
    du = u2 - u1
    ddv = dv2 - dv1
    de = e2 - e1
    dy = y2 - y1

    A = (1/2)*(dZ/Z)

    B = (1/2)*(da/a - (2*B/a)**2*du/u + (ddv + 2*(2*B/a)**2*dy)*np.sin(az)**2)

    C = (1/2)*(da/a + de*np.cos(az)**4 + ddv*np.sin(az)**2*np.cos(az)**2)

    Rpp = A + B*np.sin(theta1)**2 + C*np.sin(theta1)**2*np.tan(theta1)**2

    return(Rpp)


def tsvankin_ortho():
    return None


def elastic_impedance(Vp, Vs, p, theta):
    """
    Calculate the incidence-angle dependent elastic impedance of
    a material. Uses the Aki and Richards approximation for
    isotropic reflection coefficients.
    """
    K = (Vs/Vp)**2
    Ie = (Vp**(1 + np.tan(theta)**2) *
          p**(1 - 4*K*np.sin(theta)**2) *
          Vs**(-8*K*np.sin(theta)**2))

    return(Ie)


def extended_elastic_impedance(Vp, Vs, p, chi, Vp0=1, Vs0=1, p0=1):
    """
    Calculate the Extended Elastic Impedance of Whitcombe [2002] of a material.
    """
    K = (Vs/Vp)**2
    Iee = ((Vp0 * p0) *
           (Vp / Vp0)**(np.cos(chi) + np.sin(chi)) *
           (p / p0)**(np.cos(chi) - 4*K*np.sin(chi)) *
           (Vs / Vs0)**(-8*K*np.sin(chi)))

    return(Iee)


def exact_hti(vp1, vs1, p1, e1, d1, y1,
              vp2, vs2, p2, e2, d2, y2, theta1):
    """
    Calculate the exact Zoeppritz equations for an HTI medium using the
    Schoenberg and Protazio [1992] formulation.
    """

    C = Cij(e1, d1, y1, p1, vp1, vs1)
    Cp = Cij(e2, d2, y2, p2, vp2, vs2)

    # Horizontal and vertical slownesses
    s1 = 1 / (vp1*np.sin(theta1))
    s3 = 1 / (vp1*np.cos(theta1))
    s3p = np.sqrt(vp1**-2 - s1**2)
    s3s = np.sqrt(vs1**-2 - s1**2)

    # Eigenvectors to the roots of the anellipticity biquadratic equation
    E2 = (C[0][0] - C[4][4])*(C[2][2] - C[4][4]) - (C[0][2] + C[4][4])**2
    A = C[2][2]*C[4][4]
    B = ((C[4][4]*(C[0][0] + C[2][2]) + E2)*s1**2 - p*(C[3][3] + C[4][4]))
    C = (C[0][0]*s1**2 - p)*(C[0][0]*s1**2 - p)
    
    # Compute the two roots of the quadratic formed after variable substitution
    z1 = (-B - np.sqrt(B**2 - 4*A*C)) / (2*A)
    z2 = (-B + np.sqrt(B**2 - 4*A*C)) / (2*A)
    if z1 < z2:
        s3p = np.sqrt(z1)
        s3s = np.sqrt(z2)
    else:
        s3p = np.sqrt(z2)
        s3s = np.sqrt(z1)

    ep1 = 1
    ep3 = 1
    es1 = 1
    es3 = 1

    # Impedance matrices of upper medium
    X = np.zeros(shape=(2, 2))
    Y = np.zeros(shape=(2, 2))
    X[0][0] = ep1
    X[0][1] = es1
    X[1][0] = -(C[0][2]*s1*ep1 + C[2][2]*s3p*ep3)
    X[1][1] = -(C[0][2]*s1*es1 + C[2][2]*s3s*es3)

    Y[0][0] = -C[4][4]*(s1*ep3 + s3p*ep1)
    Y[0][1] = -C[4][4]*(s1*es3 + s3s*es1)
    Y[1][0] = ep3
    Y[1][1] = es3

    # Impedance matrices of lower medium
    Xp = np.zeros(shape=(2, 2))
    Yp = np.zeros(shape=(2, 2))
    Xp[0][0] = ep1
    Xp[0][1] = es1
    Xp[1][0] = -(Cp[0][2]*s1*ep1 + Cp[2][2]*s3p*ep3)
    Xp[1][1] = -(Cp[0][2]*s1*es1 + Cp[2][2]*s3s*es3)

    Yp[0][0] = -Cp[4][4]*(s1*ep3 + s3p*ep1)
    Yp[0][1] = -Cp[4][4]*(s1*es3 + s3s*es1)
    Yp[1][0] = ep3
    Yp[1][1] = es3

    R = (np.invert
         (np.invert(Yp)*Y + np.invert(Xp)*X) *
         (np.invert(Yp)*Y - np.invert(Xp)*X))

    return(R[0][0])
