# -*- coding: utf-8 -*-
import time
import numpy as np

class OnlineCVB0:

    def __init__(self, C, W, K, alpha, eta, tau_phi, kappa_phi, s_phi, tau_theta,
                 kappa_theta, s_theta, burn_in):
        print "initializing OnlineCVB0 algorithm ..."
        self.C = int(C)
        self.W = int(W)
        self.K = int(K)
        self.alpha = alpha
        self.eta = eta
        self.eta_sum = K * eta
        self.tau_phi = tau_phi
        self.kappa_phi = kappa_phi
        self.s_phi = s_phi
        self.tau_theta = tau_theta
        self.kappa_theta = kappa_theta
        self.s_theta = int(s_theta)
        self.burn_in = int(burn_in)
        self.updatect = 1

        self.N_phi = np.random.rand(K, W)
        self.N_Z = self.N_phi.sum(axis = 1)

    def static_online(self, wordtks, lengths):
        # E step
        start1 = time.time()
        (N_phi, N_Z, N_theta) = self.e_step(wordtks, lengths)
        end1 = time.time()
        # M step
        start2 = time.time()
        self.m_step(N_phi, N_Z)
        end2 = time.time()
        return(end1 - start1, end2 - start2, N_theta)

    def e_step(self, wordtks, lengths):
        batch_size = len(lengths)
        N_phi = np.zeros((self.K, self.W), dtype = float)
        N_Z = np.zeros(self.K)
        N_theta = np.random.rand(batch_size, self.K)
        # inference
        denominator = self.N_Z + self.eta_sum
        multiplier = self.C / sum(lengths)
        # for each document j im M
        for j in range(batch_size):
            # for zero or more "burn in" passes
            for b in range(self.burn_in):
                # for each token i
                for i in range (lengths[j]):
                    # update gamma_ij
                    gamma_ij = self.N_phi[:,wordtks[j][i]] + self.eta
                    numerator = N_theta[j] + self.alpha
                    gamma_ij = gamma_ij * numerator / denominator
                    gamma_ij = gamma_ij / sum(gamma_ij)
                    # update N_theta
                    rhot = self.s_theta * pow(self.tau_theta + i + 1, -self.kappa_theta)
                    N_theta[j] = (1 - rhot) * N_theta[j] + rhot * lengths[j] * gamma_ij
            # for each token i
            for i in range (lengths[j]):
                # update gamma_ij
                gamma_ij = self.N_phi[:,wordtks[j][i]] + self.eta
                numerator = N_theta[j] + self.alpha
                gamma_ij = gamma_ij * numerator / denominator
                gamma_ij = gamma_ij / sum(gamma_ij)
                # update N_theta
                rhot = self.s_theta * pow(self.tau_theta + i + 1, -self.kappa_theta)
                N_theta[j] = (1 - rhot) * N_theta[j] + rhot * lengths[j] * gamma_ij
                temp = multiplier * gamma_ij
                # N_w_ij(phi) := N_w_ij(phi) + C / |M| * gamma_ij
                N_phi[:,wordtks[j][i]] += temp
                # N_Z := N_Z + C / |M| * gamma_ij
                N_Z += temp
        return(N_phi, N_Z, N_theta)

    def m_step(self, N_phi, N_Z):
        rhot = self.s_phi * pow(self.tau_phi + self.updatect, -self.kappa_phi)
        self.rhot_phi = rhot
        self.N_phi *= (1 - rhot)
        self.N_phi += rhot * N_phi
        self.N_Z *= (1- rhot)
        self.N_Z += rhot * N_Z
        self.updatect += 1
