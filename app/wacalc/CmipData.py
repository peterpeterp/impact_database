# Copyright (C) 2014 Matthias Mengel and Mahe Perette
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


""" load cmip3 or cmip5 data to dimarray

Model output from the CMIP3 archive, processed by matthais.mengel (at) pik-potsdam.de
Model output from the CMIP5 archive, processed by mahe.perrette (at) pik-potsdam.de

"""

import os, glob
import numpy as np
import dimarray as da
import hadcrut_warming; reload(hadcrut_warming)
import bisect

class CmipDataException(Exception):
  pass


class CmipData():

  def __init__(self,cmip,models,scenarios):

    cmip3_path = "../../data/cmip3_ver002/"
    cmip5_path = "../../data/cmip5_ver002/"
    cmip_path  = {"CMIP3":cmip3_path,"CMIP5":cmip5_path}

    self.cmip_path  = cmip_path[cmip]
    self.cmip       = cmip
    self.models     = [x.encode('UTF8') for x in models]
    self.scenarios  = [x.encode('UTF8') for x in scenarios]

  def get_cmip(self):

    # check for availability
    localpath = os.path.join(os.path.dirname(__file__), self.cmip_path)
    fnames    = glob.glob(localpath+'/*.nc')
    print fnames
    assert fnames != [], 'no model files available'

    runs = {"CMIP3":["run1","run2","run3","run4","run5","magicc6"],
            "CMIP5":["r1i1p1","r2i1p1","r3i1p1","r4i1p1","r5i1p1"]}

    modeldata  = []
    modelavail = []
    for model in self.models:
      scendata  = []
      scenrids  = []
      scenavail = []
      for scen in self.scenarios:
        for run in runs[self.cmip]:

          # strip the star * from magicc6 emulated scens
          rid = ".".join([model,scen.strip("*"),run])
          try:
            fname = localpath+"/"+rid+".merged.nc"
            if os.path.exists(fname):
              data = da.read_nc(fname, "tas_global", verbose=True)

              scendata.append(data)
              scenrids.append(rid)
              scenavail.append(scen)
            # do not read further runs of this model scen combination if successful
              break
          except IOError, msg:
            print msg, "==> skip."

      if scendata == []: continue
      # merge scenarios of one model
      modeldata.append(da.from_arrays(scendata, keys=scenavail, axis='scenario'))
      modelavail.append(model)

    # merge all models
    try:
      alldata = da.from_arrays(modeldata, keys=modelavail, axis='model')
      print alldata
    except IndexError:
      raise CmipDataException("No model data available for your choice.")

    # time from months to years.
    alldata.axes["time"].values= alldata.axes["time"].values/12
    alldata = alldata.swapaxes("model",1)

    self.gmt        = alldata
    self.modelavail = modelavail


  def compute_warming(self, preindp, basep, finalp):
    """ Compute warming between baseperiod bp and endperiod ep for CMIP GCMs """

    self.gmt = self.gmt.mean(axis='model',skipna=True)
    self.gmt = self.gmt.swapaxes('time',0)

    warming_since_preind = hadcrut_warming.get_warming(basep, preindp)

    try:
      # TODO: we should better track which models kicked out at this step.
      anom = self.gmt[finalp[0]:finalp[1]].mean(axis=0) - self.gmt[basep[0]:basep[1]].mean(axis=0)

    except IndexError:
      per = str(self.gmt.axes["time"][0]) + " and "+str(self.gmt.axes["time"][-1])+"."
      raise CmipDataException("at least one period seems to be out of range, chose between "+per)

    self.anom         = anom
    self.warming_attr = anom + warming_since_preind
    self.w_preind     = warming_since_preind


  def create_wb3_wlevel_forhtml(self, warming_levels_wb3, warming_level_names):

    self.htmlparse_scen = []
    self.htmlparse_anom = {}
    self.htmlparse_attribution   = {}
    self.htmlparse_wb3lev = {}
    self.htmlparse_wb3num = {}

    for i, m in enumerate(self.warming_attr.labels[0]):

      self.htmlparse_scen.append(m)

      attr = self.warming_attr.values[i]
      self.htmlparse_anom[m] = self.anom.values[i]

      attr = self.warming_attr.values[i]
      self.htmlparse_attribution[m] = attr
      print warming_levels_wb3, attr
      self.htmlparse_wb3num[m] = bisect.bisect_left(warming_levels_wb3,attr)
      print self.htmlparse_wb3num[m]
      self.htmlparse_wb3lev[m] = warming_level_names[self.htmlparse_wb3num[m]]

    self.emulator_used = False
    print "++++++", self.htmlparse_scen
    if "sresa1fi*" in self.htmlparse_scen or "sresb2*" in self.htmlparse_scen:
      self.emulator_used = True

    print   "++++++", self.emulator_used


  def __running_mean(self, gmt, window):

    def _running_mean(x, N):
      """ running mean with masked out boundaries, signal in middle of array """
      assert window % 2 == 1 # is odd
      rmean = np.ma.array(x,copy=True,mask=True)
      rmean[(N/2):-(N/2)] = np.convolve(x, np.ones((N,))/N,"valid")
      return rmean

    assert gmt.dims[0] == "time"

    vals = np.ma.array(gmt.values,copy=True,mask=True)
    for i in range(0,vals.shape[1]):
      for j in range(0,vals.shape[2]):
        vals[:,i,j] = _running_mean(gmt.values[:,i,j],window)

    gmt.values = vals
    return gmt


  def compute_period(self, basep, preindp, warminglevs, window=3):

    self.gmt = self.gmt.swapaxes('time',0)

    # the model warming anomaly from its base period
    self.gmt = self.gmt - self.gmt[basep[0]:basep[1]].mean(axis=0)

    # the observed warming from preindustrial to baseperiod
    warming_since_preind = hadcrut_warming.get_warming(basep, preindp)
    # constructed warming from observed plus projected
    self.gmt = self.gmt + warming_since_preind

    # smoothing and model mean.
    gmt_smooth    = self.__running_mean(self.gmt, window)
    gmt_mm_smooth = gmt_smooth.mean(axis="model", skipna=True)

    gmttime  = np.array(self.gmt.axes["time"])

    times_mm = da.DimArray(axes=[
      ("scenario",list(self.gmt.axes["scenario"])),
      ("wlevel",   warminglevs)
      ])

    self.emulator_used = False

    for lev in warminglevs:
      for scen in self.gmt.scenario:

        gtt = gmt_mm_smooth[:, scen]
        warming_exceeded = gmt_mm_smooth[:, scen] >= lev

        try:
          times_mm[scen, lev] = gmttime[warming_exceeded.values][0]
        except IndexError, e:
          print str(e)
          print "modelmean does not exceed",lev,"in scenario", scen, "."

      if scen in ["sresa1fi*","sresb2*"]:
        self.emulator_used = True

    self.exceedance_tm = times_mm


######## end of class.


if __name__ == "__main__":
    """
    """
    print "DEBUG: CHECKING "+ __file__
    print ""
    import settings; reload(settings)
    cmip3path = "../../data/cmip3_ver001/"
    cmip5path = "../../data/cmip5_ver001/"
    cmipdata = CmipData("CMIP5",settings.cmip5_models[0:4], settings.cmip5_scenarios[0:3])
    cmipdata.get_cmip()
    cmipdata.compute_warming( settings.preind_period, settings.baseperiod, settings.finalperiod)



