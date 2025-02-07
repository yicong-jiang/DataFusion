from tool/csb import *
from tool/util import *
from 4_1_2/data_generate import *
from 4_1_2/LogNorm import *



def simu_lognorm(W_p = 0.5,
            sigmae_list = list(np.array(range(1, 11)) * 0.1)):

    for sigmae in sigmae_list:
        sigma = sigmae
        repli_number = 1000
        res_width_csb = np.zeros(repli_number)
        res_width_dbnd = np.zeros(repli_number)
        res_width_csb_cof = np.zeros(repli_number)
        res_width_dbnd_cof = np.zeros(repli_number)
        res_l_csb = np.zeros(repli_number)
        res_u_csb = np.zeros(repli_number)
        res_l_csb_ci = np.zeros(repli_number)
        res_u_csb_ci = np.zeros(repli_number)
        res_l_dbnd = np.zeros(repli_number)
        res_u_dbnd = np.zeros(repli_number)
        res_l_dbnd_ci = np.zeros(repli_number)
        res_u_dbnd_ci = np.zeros(repli_number)
        

        for i in range(repli_number):
            dgp_seed = i + 1
            my_data = gen_ols_data_lognorm_new(n = 1000, p = 20, W_p = 0.5, sigma= sigma, sigmae = sigmae, dgp_seed=dgp_seed)
            data = my_data
            data['y'] = data['Y'] * data['W'] + data['S'] * (1 - data['W'])

            csb = cauchy_schwarz_modified(
                            covariates=data['X'], 
                            treatment=data['W'], 
                            outcome=data['y'],
                            nfolds = 20,
                            rprobs = data['pis'], rfit = True)
            csb_res = csb.fit(LognormalRidge(), LognormalRidge(), LogisticRegressionCV())


            dbnd = DualBounds(
                        f=lambda y0, y1, x: y0 * y1, # defines the estimand
                        covariates=data['X'], # n x p covariate matrix
                        treatment=data['W'], # n-length treatment vector
                        outcome=data['y'], # n-length outcome vector
                        #propensities=data['pis'], # n-length propensity scores (optional)
                        outcome_model=LognormalRidge, # description of model for Y | X, W
                        heterosked_model=LognormalRidge,
            )


            dbnd.fit(
                            nfolds=20, # number of cross-fitting folds
                            #alpha=0.05, # nominal level,
                            verbose=True # show progress bars
            )

            dbnd_res = dbnd.results()

            res_width_csb[i] = csb.print_result()['Upper'].iloc[0] - csb.print_result()['Lower'].iloc[0] - 2 * sigma *sigmae
            res_width_dbnd[i] = dbnd_res['Upper'].iloc[0] - dbnd_res['Lower'].iloc[0] - 2 * sigma *sigmae
            res_width_csb_cof[i] = csb.print_result()['Upper'].iloc[2] - csb.print_result()['Lower'].iloc[2] - 2 * sigma *sigmae
            res_width_dbnd_cof[i] = dbnd_res['Upper'].iloc[2] - dbnd_res['Lower'].iloc[2] - 2 * sigma *sigmae
            res_l_csb[i] = csb.print_result()['Lower'].iloc[0]
            res_u_csb[i] = csb.print_result()['Upper'].iloc[0]
            res_l_csb_ci[i] = csb.print_result()['Lower'].iloc[2]
            res_u_csb_ci[i] = csb.print_result()['Upper'].iloc[2]
            res_l_dbnd[i] = dbnd_res['Lower'].iloc[0]
            res_u_dbnd[i] = dbnd_res['Upper'].iloc[0]
            res_l_dbnd_ci[i] = dbnd_res['Lower'].iloc[2]
            res_u_dbnd_ci[i] = dbnd_res['Upper'].iloc[2]
        
        res_dataset = [res_l_csb, res_u_csb,
                            res_l_csb_ci, res_u_csb_ci, 
                            res_l_dbnd, res_u_dbnd,
                            res_l_dbnd_ci, res_u_dbnd_ci,
                            time_csb, time_dbnd]

        return res_dataset




