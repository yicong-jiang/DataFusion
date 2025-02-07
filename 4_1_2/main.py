from tool/csb import *
from tool/util import *
from tool/cov_wid_cal import *
from 4_1_2/data_generate import *
from 4_1_2/simu import *


if __name__ == "__main__":
    res_dataset = simu_lognorm()
    cov_wid_cal(res_dataset = res_dataset, filename = '4_1_2')
