import dualbounds as db
import numpy as np
import pandas as pd
from dualbounds.generic import DualBounds
from numpy.linalg import inv
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import LinearRegression
import collections
import inspect
import time
import matplotlib.pyplot as plt


def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class ols_preprocessing:
    def save_hyperparameters(self, ignore=[]):
        frame = inspect.currentframe().f_back
        _, _, _, local_vars = inspect.getargvalues(frame)
        self.hparams = {k:v for k, v in local_vars.items() 
                        if k not in set(ignore+['self']) and not k.startswith('_')}
        for k, v in self.hparams.items():
            setattr(self, k, v)

    
    def __init__(self, 
                 dgp_seed,
                 n = 100,
                 rho = 0,
                 tau = 0.3,
                 beta1 = 0.5,
                 beta2 = 0.5,
                 sigmae = 1,
                 sigma = 1,
                 alpha = 0.05,
                 nfolds = 2):
        self.save_hyperparameters()
        ma_cov = np.zeros((5, 5))
        ma_cov[0][0] = beta1 * beta1 + beta2 * beta2 + 2 * rho * beta1 * beta2 + sigmae * sigmae
        ma_cov[0][1] = beta1 + rho * beta2
        ma_cov[0][2] = beta1 * rho + beta2
        ma_cov[0][3] = beta1 + rho * beta2
        ma_cov[0][4] = beta1 * rho + beta2

        ma_cov[1][0] = beta1 + rho * beta2
        ma_cov[1][1] = 1 + sigma * sigma
        ma_cov[1][2] = rho + tau * sigma * sigma
        ma_cov[1][3] = 1
        ma_cov[1][4] = rho

        ma_cov[2][0] = beta1 * rho + beta2
        ma_cov[2][1] = rho + tau * sigma * sigma
        ma_cov[2][2] = 1 + sigma * sigma
        ma_cov[2][3] = rho
        ma_cov[2][4] = 1

        ma_cov[3][0] = beta1 + rho * beta2
        ma_cov[3][1] = 1
        ma_cov[3][2] = rho
        ma_cov[3][3] = 1
        ma_cov[3][4] = rho

        ma_cov[4][0] = beta1 * rho + beta2
        ma_cov[4][1] = rho
        ma_cov[4][2] = 1
        ma_cov[4][3] = rho
        ma_cov[4][4] = 1

        self.ma_cov = ma_cov

        beta_z = np.array([1 / (1 - rho * rho), - rho / (1 - rho * rho)])

        cov_YX = ma_cov[0, 1:3]
        cov_YY = ma_cov[0, 0]
        cov_XX = ma_cov[1:3, 1:3]

        cov_ZZ = beta_z @ ma_cov[3:, 3:] @ beta_z
        cov_ZX = beta_z @ ma_cov[3:, 1:3]

        self.bound_theo_lower = cov_YX @ inv(cov_XX) @ cov_ZX - np.sqrt(cov_YY - cov_YX @ inv(cov_XX) @ cov_YX) * np.sqrt(cov_ZZ - cov_ZX @ inv(cov_XX) @ cov_ZX)
        self.bound_theo_upper = cov_YX @ inv(cov_XX) @ cov_ZX + np.sqrt(cov_YY - cov_YX @ inv(cov_XX) @ cov_YX) * np.sqrt(cov_ZZ - cov_ZX @ inv(cov_XX) @ cov_ZX)

    def data_gen_(self):
        self.data =  gen_ols_data_high(
            n = self.n,
            rho = self.rho,
            tau = self.tau,
            beta1 = self.beta1,
            beta2 = self.beta2,
            sigmae = self.sigmae,
            sigma = self.sigma,
            dgp_seed = self.dgp_seed)
        self.data['y'] = self.data['W'] * self.data['Y'] + (1 - self.data['W']) * self.data['S']        
