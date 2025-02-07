# DataFusion
Code for "Semiparametric inference for partially identifiable data fusion estimands via double machine learning"

To run the code, one first need to install the python package <code>dualbounds</code>. RUn the following code for installation:

<code>python -m pip install dualbounds </code>

Before running the code, please first set the working directory to be <code>DataFusion</code> folder.

The code for Section 4.1.1, the simulation result on linear model, is located in folder <code>4.1.1</code>. The code consists of three parts: <code>4.1.1/data_generate.py</code> generate the data for simulation, <code>4.1.1/simu.py<code defines the simulation process, and <code>4.1.1/main.py<code generates the results, which is expected to be two csv files, one containing the Monte Carlo statistics (e.g., mean and standard deviation) for the coverage of our method's and Dualbounds' confidence bounds throughout the repeated experiments,  and the other for the width of the bounds. To run the code, simply run <code>4.1.1/main.py<code. To visualize the result, one may use <code>plot.R<code to generate the result.

Similarly, the code for Section 4.1.2, the simulation result on average relative treatment effect, is located in folder <code>4.1.2</code>. The code consists of four parts: <code>4.1.2/data_generate.py<code generate the data for simulation, <code>4.1.2/LogNorm.py<code defines the <code>sklearn<code friendly class for estimating the mean and varaince of log-Normal distribution, <code>4.1.2/simu.py<code defines the simulation process, and <code>4.1.2/main.py<code generates the results, which is expected to be two csv files, one containing the Monte Carlo statistics (e.g., mean and standard deviation) for the coverage of our method's and Dualbounds' confidence bounds throughout the repeated experiments,  and the other for the width of the bounds. To run the code, simply run <code>4.1.2/main.py<code. To visualize the result, one may use <code>plot.R<code to generate the result.

The code for Section 4.2, relating consumption to wealth, is located in folder <code>4.2</code>. For the result on the ordinary least squares coefficient $\beta_Z$, one can run <code>main.R<code. Note that for different machince learning methods and clipping options, one may need to modify the code accordingly. For comparison with Dualbounds, one can run <code>main.py<code.

