from tool/csb import *
from tool/util import *
from tool/cov_wid_cal import *
from 4_1_1/data_generate import *
from 4_1_1/simu import *


if __name__ == "__main__":
    res_dataset = simu_ols()
    cov_wid_cal(res_dataset = res_dataset, filename = '4_1_1')
