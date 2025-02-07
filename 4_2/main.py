from tool/csb import *
from tool/util import *
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import LogisticRegressionCV
from sklearn.linear_model import LogisticRegression

if __name__ == "__main__":
    np.random.seed(17)
    data_real_2 = pd.read_csv("./4_2/real_3.csv")
    data_real_2 = data_real_2.sample(frac = 1)


    # linear model
    print("Linear model")
    print('*' * 32)

    pro_est = LogisticRegressionCV()
    pro_est.fit(data_real_2[['SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME']], data_real_2['R'])
    pis_est = pro_est.predict_proba(data_real_2[['SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME']], )[:, 1]
    pis_est[pis_est <= 0.05] = 0.05
    pis_est[pis_est >= 0.95] = 0.95

    cur_time = time.time()
    np.random.seed(107)
    dbnd_real_2 = DualBounds(
                f=lambda y0, y1, x: y0 * y1, # defines the estimand
                covariates=data_real_2[['SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME']], # n x p covariate matrix
                treatment= data_real_2['R'], # n-length treatment vector
                outcome= data_real_2['EXPEND'] * data_real_2['R'] + data_real_2['NWORTH'] * (1 - data_real_2['R']), # n-length outcome vector
                #propensities=data['pis'], # n-length propensity scores (optional)
                propensities= pis_est,
                outcome_model=LinearRegression, # description of model for Y | X, W
                heterosked_model= RandomForestRegressor
    )


    dbnd_real_2.fit(
            nfolds=20, # number of cross-fitting folds
            alpha=0.05, # nominal level,
            verbose=True # show progress bars
    )
    print("The running time of db is {}.".format(time.time() - cur_time))
    print(dbnd_real_2.results())

    alpha = 0.05
    np.random.seed(107)
    csb_2 = cauthy_schwartz(
                    covariates = np.array(data_real_2[['SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME']]), # n x p covariate matrix
                    treatment = np.array(data_real_2['R']), # n-length treatment vector
                    outcome = np.array(data_real_2['EXPEND'] * data_real_2['R'] + data_real_2['NWORTH'] * (1 - data_real_2['R'])), # n-length outcome vector
                    nfolds = 20)
    csb_res_2 = csb_2.fit(LinearRegression(), LinearRegression(), 
                        LogisticRegression(), 
                        Y_v_model=RandomForestRegressor(),
                        Z_v_model=RandomForestRegressor(),
                        rfit = True, clip = 0.05)
    print("The running time of our method is {}.".format(csb_2.runtime))
    print(csb_2.print_result()) 

    print('*' * 32)


    #random forest
    print("Random forest")
    print('*' * 32)

    np.random.seed(107)
    cur_time = time.time()

    dbnd_real_2_1 = DualBounds(
                f=lambda y0, y1, x: y0 * y1, # defines the estimand
                covariates=data_real_2[['SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME']], # n x p covariate matrix
                treatment= data_real_2['R'], # n-length treatment vector
                outcome= data_real_2['EXPEND'] * data_real_2['R'] + data_real_2['NWORTH'] * (1 - data_real_2['R']), # n-length outcome vector
                #propensities=data['pis'], # n-length propensity scores (optional)
                propensities= pis_est,
                outcome_model='randomforest', # description of model for Y | X, W
                heterosked_model='randomforest',
    )


    dbnd_real_2_1.fit(
            nfolds=2, # number of cross-fitting folds
            #alpha=0.05, # nominal level,
            verbose=True # show progress bars
    )
    print("The running time of db is {}.".format(time.time() - cur_time))
    print(dbnd_real_2_1.results())

    np.random.seed(107)
    csb_2_1 = cauthy_schwartz(
                    covariates = np.array(data_real_2[['SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME']]), # n x p covariate matrix
                    treatment = np.array(data_real_2['R']), # n-length treatment vector
                    outcome = np.array(data_real_2['EXPEND_demean'] * data_real_2['R'] + data_real_2['NWORTH_demean'] * (1 - data_real_2['R'])), # n-length outcome vector
                    nfolds = 2)
    _ = csb_2_1.fit(RandomForestRegressor(), RandomForestRegressor(), LogisticRegressionCV(),
                    RandomForestRegressor(), RandomForestRegressor(),
                    rfit = True, clip = 0.05)
    print("The running time of our method is {}.".format(csb_2_1.runtime))
    print(csb_2_1.print_result())

