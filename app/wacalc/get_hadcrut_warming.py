
def get_warming_rel_hadcrutdata(base_period,pre_ind_period=[1851,1879]):
	"""
	    :type base_period: list
	    :param base_period: baseline period of interest, contains two elements: startyear and endyear

	    :type preind_period: list
	    :param preind_period: preindustrial period, contains two elements: startyear and endyear
	    					  default= 1850 - 1879


	    :returns: Mean GMT warming for given base_period rel to pre-industrial

	    DATA SOURCE:
		Read in the Hadcrut4 GMT best estimate time series
		Source:
		http://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/download.html
		Manual:
		http://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/series_format.html

		Time series are presented as temperature anomalies (deg C) relative to 1961-1990
		First Column: date
		Second Column: median out of the 100 ens members
	"""
	import numpy as np 
	hcdat=np.loadtxt('data/hadcrut4_ts.dat',usecols=[0,1])

	pre_ind_vec=[hcdat[:,0]>=pre_ind_period[0]][0]*[hcdat[:,0]<=pre_ind_period[1]][0]
	pre_ind_mean=hcdat[pre_ind_vec][:,1].mean()

	bs_line_vec=[hcdat[:,0]>=base_period[0]][0]*[hcdat[:,0]<=base_period[1]][0]
	bs_line_mean=hcdat[bs_line_vec][:,1].mean()

	return bs_line_mean - pre_ind_mean





