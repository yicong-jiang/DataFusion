from tool/util import *

def gen_ols_data(
    n = 2000,
    rho = 0,
    tau = 0.3,
    beta1 = 1,
    beta2 = 1,
    sigmae = 0.5,
    sigma = 0.5,
	dgp_seed=1,
):
    np.random.seed(dgp_seed)
    # sample Z
    Z1 = np.random.randn(n)
    Z2 = np.random.randn(n)
    Z2 = rho * Z1 + np.sqrt(1 - rho * rho) * Z2
    S = (Z1 - rho * Z2) / (1 - rho * rho)
    
    # sample Wer
    Wer1 = np.random.randn(n) * sigma
    Wer2 = np.random.randn(n) * sigma
    Wer2 = tau * Wer1 + np.sqrt(1 - tau * tau) * Wer2
    
    # sample X
    X1 = Z1 + Wer1
    X2 = Z2 + Wer2
    X = np.vstack((X1, X2)).T
    
    # sample Y
    Y = beta1 * Z1 + beta2 * Z2 + np.random.randn(n) * sigmae
    
    
    #sample W
    W = np.random.binomial(1, 0.5 * np.ones(n))
    
    return dict(
        Y = Y, 
        W = W,
        X = X,
        S = S,
        Z1 = Z1,
        Z2 = Z2,
    )
