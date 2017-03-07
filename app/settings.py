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




""" database setting file. """



import os
import numpy as np


try:
    import bibtex_reader as bibtex_reader; reload(bibtex_reader)
except ImportError:
    raise ImportError(
        "cannot find bibtex_reader code")


bibtex=open('impact_reference_v1.1.bib','r').read().split('@')

bib=bibtex_reader.bibliography()
for entry in bibtex:
	bib.add_article(entry)

keywords=bib._meta['keywords'].keys()
regions=list(filter(lambda x: (x.lower() in ['west africa','caribbean','pacific']),keywords))
thematics=list(filter(lambda x: (x.lower() in ['climate information','impact & vulnerability of natural resources','impact & vulnerability of socio-economic systems at regional, national and sub-national scale','impact & vulnerability of livelihoods at community and household level','adaptation']),keywords))
types=list(filter(lambda x: (x.lower() in ['peer reviewed','seminal','grey literature']),keywords))
unsorteds=list(filter(lambda x: (x.lower() not in regions+thematics+types),keywords))

