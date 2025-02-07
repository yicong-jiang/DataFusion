from tool/csb import *
from tool/util import *
from 4_1_1/data_generate import *
import pickle

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
sigma= 0.2
sigmae = 2
W_p = 0.5

for i in range(repli_number):
    dgp_seed = i + 1
    my_data = gen_ols_data_high(n = 1000, p = 20, W_p = W_p, sigma= sigma, sigmae = sigmae, dgp_seed=dgp_seed)
    data = my_data
    data['y'] = data['Y'] * data['W'] + data['S'] * (1 - data['W'])
    csb = cauthy_schwartz(
                covariates=data['X'], # n x p covariate matrix
                treatment=data['W'], # n-length treatment vector
                outcome=data['y'],# n-length outcome vector
                nfolds = 2)
    csb_res = csb.fit(RidgeCV(alphas = 0.05), RidgeCV(alphas = 0.05))

    data['pis'] = 0.5 * np.ones(len(data['W']))
    dbnd = DualBounds(
            f=lambda y0, y1, x: y0 * y1, # defines the estimand
            covariates=data['X'], # n x p covariate matrix
            treatment=data['W'], # n-length treatment vector
            outcome=data['y'], # n-length outcome vector
            propensities=data['pis'], # n-length propensity scores
            outcome_model='ridge', # description of model for Y | X, W
     )


    dbnd.fit(
                nfolds=2, # number of cross-fitting folds
                alpha=0.05, # nominal level,
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
    
res_dataset = [res_l_csb,
res_u_csb,
res_l_csb_ci,
res_u_csb_ci,
res_l_dbnd,
res_u_dbnd,
res_l_dbnd_ci,
res_u_dbnd_ci]

outputFile = '4_1_1.pickle'
fw = open(outputFile, 'wb')
pickle.dump(res_dataset, fw)
fw.close()
