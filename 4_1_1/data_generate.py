from tool/util import *

def gen_ols_data_high(
    n = 2000,
    p = 50,
    rho = 0,
    tau = 0.3,
    beta1 = 1,
    beta2 = 1,
    sigmae = 0.5,
    sigma = 0.5,
	dgp_seed=1,
    W_p = 0.5,
):
    np.random.seed(dgp_seed)
  
    # sample beta
    #beta_Y = np.random.randn(p) / np.sqrt(p) 
    #beta_Z = np.random.randn(p) / np.sqrt(p)
    beta = np.random.randn(p)
    beta = beta / np.sqrt(np.sum(beta ** 2))

    # sample X
    #print(np.matrix(np.ones(p)).transpose() @ np.matrix(beta))
    X = 0.5 * np.random.randn(n * p).reshape((n, p)) 


    # sample Z
    W_Z = np.random.randn(n)
    t_z = 1
    #W_Z = W_Z ** 3 / np.sqrt(15) #* np.abs(W_Z)
    #W_Z = (np.exp(t_z * W_Z) - np.exp(0.5 * t_z * t_z)) / np.sqrt(np.exp(2 * t_z * t_z) - np.exp(t_z * t_z))

    S = np.sqrt(0.75) + (X @ beta)  + sigma * W_Z

    
    # sample Y
    W_Y = np.random.randn(n)
    t_y = 1
    #W_Y = W_Y ** 3 / np.sqrt(15) #* np.abs(W_Y)
    #W_Y = (np.exp(t_y * W_Y) - np.exp(0.5 * t_y * t_y)) / np.sqrt(np.exp(2 * t_y * t_y) - np.exp(t_y * t_y))
    #W_Y = (np.exp(W_Y) - np.exp(0.5)) / np.sqrt(np.exp(2) - np.exp(1))

    Y = np.sqrt(0.75) + (X @ beta) + sigmae * W_Y

    
    
    #sample W
    W = np.random.binomial(1, W_p * np.ones(n))

    
    return dict(
        Y = Y, 
        W = W,
        X = X,
        S = S,
        W_Z = W_Z,
        W_Y = W_Y,
        beta = beta,
    )
