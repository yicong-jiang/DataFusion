from tool/util import *

class cauchy_schwarz_modified:
    def __init__(self, covariates, treatment, outcome, nfolds, rprobs, rfit = False):
        self.X = covariates
        self.R = treatment
        self.YZ = outcome
        self.n = self.R.shape[0]
        self.nfolds = nfolds
        self.rprob = rprobs
        self.rfit = rfit


    def fit(self, Y_model, Z_model, R_model):
        cur_time = time.time()
        fold_len = self.n // self.nfolds
        fold_start = np.array(range(self.nfolds)) * fold_len
        fold_end = np.array(range(1, self.nfolds + 1)) * fold_len
        fold_end[-1] = self.n

        bounds_lower = np.zeros(self.n)
        bounds_upper = np.zeros(self.n)

        for nstart, nend in zip(fold_start, fold_end):
            mask = np.zeros(self.n)
            mask[nstart:nend] = 1
            
            model_YX = Y_model.fit(self.X[(self.R == 1) & (mask == 0), ], self.YZ[(self.R == 1) & (mask == 0)])
            #self.model_YX = model_YX
            m_YX = model_YX.predict(self.X)
            #self.m_YX = m_YX
            #v_YX = np.mean((self.YZ[(self.R == 1) & (mask == 0)] - m_YX[(self.R == 1) & (mask == 0)]) ** 2)
            v_YX = model_YX.predict_var(self.X)
            
            model_ZX = Z_model.fit(self.X[(self.R == 0) & (mask == 0), ], self.YZ[(self.R == 0) & (mask == 0), ])
            #self.model_ZX = model_ZX
            m_ZX = model_ZX.predict(self.X)
            #v_ZX = np.mean((self.YZ[(self.R == 0) & (mask == 0)] - m_ZX[(self.R == 0) & (mask == 0)]) ** 2)
            v_ZX = model_ZX.predict_var(self.X)

            if self.rfit:
                model_R = R_model.fit(self.X[(mask == 0), ], self.R[(mask == 0), ])
                self.rprob = model_R.predict_proba(self.X)[:, 1]
            
            
            phi_YX_m = (self.YZ - m_YX) * m_ZX 
            phi_YX_v = 0.5 * np.sqrt(v_ZX / v_YX) * ((self.YZ - m_YX) * (self.YZ - m_YX) - v_YX)

            phi_ZX_m = (self.YZ - m_ZX) * m_YX 
            phi_ZX_v = 0.5 * np.sqrt(v_YX / v_ZX) * ((self.YZ - m_ZX) * (self.YZ - m_ZX) - v_ZX)

            M_m = m_YX * m_ZX
            M_v = np.sqrt(v_YX * v_ZX)
            #print(v_YX)

            b_lower = M_m - M_v + self.R / self.rprob * (phi_YX_m - phi_YX_v) + (1 - self.R) / (1 - self.rprob) * (phi_ZX_m - phi_ZX_v)
            b_upper = M_m + M_v + self.R / self.rprob * (phi_YX_m + phi_YX_v) + (1 - self.R) / (1 - self.rprob) * (phi_ZX_m + phi_ZX_v)
            #print(np.mean(M_m + self.R / self.rprob * (phi_YX_m) + (1 - self.R) / (1 - self.rprob) * (phi_ZX_m)))
            #print(np.mean( M_v + self.R / self.rprob * (phi_YX_v) + (1 - self.R) / (1 - self.rprob) * (phi_ZX_v)))
            #print(np.std(M_m - M_v))

            bounds_lower[mask == 1] = b_lower[mask == 1]
            bounds_upper[mask == 1] = b_upper[mask == 1]

        self.bounds_lower = bounds_lower
        self.bounds_upper = bounds_upper

        self.est_lower = np.mean(bounds_lower)
        self.est_upper = np.mean(bounds_upper)

        self.se_lower = np.std(bounds_lower) / np.sqrt(len(bounds_lower))
        self.se_upper = np.std(bounds_upper) / np.sqrt(len(bounds_upper))

        self.lcb = self.est_lower - 1.96 * np.std(bounds_lower) / np.sqrt(self.n)
        self.ucb = self.est_upper + 1.96 * np.std(bounds_upper) / np.sqrt(self.n)

        self.runtime = time.time() - cur_time

        return dict(est_lower = self.est_lower, est_upper = self.est_upper, lcb = self.lcb, ucb = self.ucb, time = self.runtime)

    
    def print_result(self):
        output_frame = pd.DataFrame([[self.est_lower, self.est_upper], [self.se_lower, self.se_upper], [self.lcb, self.ucb]], 
                                    index = ['Estimate', 'SE', 'Conf. Int.'], columns = ['Lower', 'Upper'])
        return output_frame
        
    
