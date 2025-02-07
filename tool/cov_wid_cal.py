from tool/util import *

def cov_wid_cal(res_dataset, 
                sigma = 0.2,
                sigmae_list = list(0.2 * np.array(range(1, 8))),
                filename = ""):

    coverage_csb = np.zeros(len(sigmae_list))
    coverage_csb_decap = np.zeros(len(sigmae_list))
    coverage_dbnd = np.zeros(len(sigmae_list))
    coverage_csb_l = np.zeros(len(sigmae_list))
    coverage_dbnd_l = np.zeros(len(sigmae_list))
    coverage_csb_u = np.zeros(len(sigmae_list))
    coverage_dbnd_u = np.zeros(len(sigmae_list))
    coverage_csb_std = np.zeros(len(sigmae_list))
    coverage_csb_decap_std = np.zeros(len(sigmae_list))
    coverage_dbnd_std = np.zeros(len(sigmae_list))


    width_csb = np.zeros(len(sigmae_list))
    width_dbnd = np.zeros(len(sigmae_list))
    width_csb_std = np.zeros(len(sigmae_list))
    width_dbnd_std = np.zeros(len(sigmae_list))

    width_csb_q_l = np.zeros(len(sigmae_list))
    width_dbnd_q_l = np.zeros(len(sigmae_list))

    width_csb_q_u = np.zeros(len(sigmae_list))
    width_dbnd_q_u = np.zeros(len(sigmae_list))

    width_csb_decap = np.zeros(len(sigmae_list))
    width_csb_std_decap = np.zeros(len(sigmae_list))

    width_gap = np.zeros(len(sigmae_list))
    width_gap_theo = np.zeros(len(sigmae_list))
    width_gap_std = np.zeros(len(sigmae_list))
    width_gap_theo_std = np.zeros(len(sigmae_list))

    time_csb = np.zeros(len(sigmae_list))
    time_dbnd = np.zeros(len(sigmae_list))


    for i in range(7):
        sigmae = sigmae_list[i]
        
        
        bound_lower = 1 - sigma * sigmae
        bound_upper = 1 + sigma * sigmae
        coverage_csb[i] = np.mean((res_dataset[2] < bound_lower) & (res_dataset[3] > bound_upper)) 
        coverage_csb_std[i] = np.std((res_dataset[2] < bound_lower) & (res_dataset[3] > bound_upper)) 
        
        
        width_csb[i] = np.mean(res_dataset[3] - res_dataset[2])
        width_csb_std[i] = np.std(res_dataset[3] - res_dataset[2])
        

        coverage_dbnd[i] = np.mean((res_dataset[6] < bound_lower) & (res_dataset[7] > bound_upper)) 
        coverage_dbnd_std[i] = np.std((res_dataset[6] < bound_lower) & (res_dataset[7] > bound_upper)) 

        width_dbnd[i] = np.mean(res_dataset[7] - res_dataset[6])
        width_dbnd_std[i] = np.std(res_dataset[7] - res_dataset[6])
        
        width_gap[i] = np.mean((res_dataset[3] - res_dataset[2]) - (res_dataset[7] - res_dataset[6]))
        width_gap_std[i] = np.std((res_dataset[3] - res_dataset[2]) - (res_dataset[7] - res_dataset[6]))
        
        time_csb[i] = np.mean(res_dataset[8])
        time_dbnd[i] = np.mean(res_dataset[9])
    

    coverage_dataset = pd.DataFrame({"csb": coverage_csb, 
                                    "db": coverage_dbnd, 
                                    "csb_sd": coverage_csb_std, 
                                    "db_sd": coverage_dbnd_std,
                                    "csb_decap": coverage_csb_decap, 
                                    "csb_decap_std": coverage_csb_decap_std})

    width_dataset = pd.DataFrame({"csb": width_csb, 
                                "db": width_dbnd, 
                                "csb_sd": width_csb_std, 
                                "db_sd": width_dbnd_std, 
                                "csb_decap": width_csb_decap, 
                                "csb_decap_std": width_csb_std_decap, 
                                "gap":width_gap, 
                                "gap_sd": width_gap_std, 
                                "gap_theo":width_gap_theo, 
                                "gap_theo_sd":width_gap_theo_std})

    coverage_dataset.to_csv("coverage_{}.csv".format(filename))
    width_dataset.to_csv("width_{}.csv".format(filename))




