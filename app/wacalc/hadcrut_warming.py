# Copyright (C) 2014 Matthias Mengel and Carl-Friedrich Schleussner
#
# This file is part of wacalc.
#
# wacalc is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# wacalc is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with wacalc; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
"""
import os
import numpy as np

relpath ='data/hadcrut_ver001/hadcrut4_ts.dat'
hadcrut_path = "/"+ reduce(os.path.join,os.path.dirname(__file__).split("/")[0:-2]+[relpath])
#print hadcrut_path

def get_warming(base_period,pre_ind_period=[1851,1879]):
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

  hcdat=np.loadtxt(hadcrut_path,usecols=[0,1])

  pre_ind_select = [hcdat[:,0]>=pre_ind_period[0]][0]*[hcdat[:,0]<=pre_ind_period[1]][0]
  pre_ind_mean   = hcdat[pre_ind_select][:,1].mean()

  bs_line_select = [hcdat[:,0]>=base_period[0]][0]*[hcdat[:,0]<=base_period[1]][0]
  bs_line_mean   = hcdat[bs_line_select][:,1].mean()

  return bs_line_mean - pre_ind_mean













