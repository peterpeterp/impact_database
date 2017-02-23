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


bibtex=open('database.bib','r').read().split('@')

bib=bibtex_reader.bibliography()
for entry in bibtex:
	bib.add_article(entry)

keywords=bib._meta['keywords'].keys()
regions=list(filter(lambda x: (x.lower() in ['west-africa','caribbean','pacific']),keywords))
thematics=list(filter(lambda x: (x.lower() in ['climate information','impact & vulnerability of natural resources','impact & vulnerability of socio-economic systems at regional, national and sub-national scale','impact & vulnerability of livelihoods at community and household level','adaptation']),keywords))
types=list(filter(lambda x: (x.lower() in ['peer-reviewd','international institution','ngo','governmental institution']),keywords))
unsorteds=list(filter(lambda x: (x.lower() not in regions+thematics+types),keywords))



# selected=bib.filter({'keywords':['pacific','caribbean']})
# word_count,list_=bib.check_occurence_of_keyword(selected)


# wc = WordCloud(background_color="white", max_words=2000,
#            stopwords=stopwords, max_font_size=40, random_state=42)#,mask=settings.world_mask

# # wc.generate_from_frequencies(word_count[0:20])
# wc.generate(' '.join(list_))


# fig = plt.figure(figsize=(20,10))
# #plt.imshow(wc.recolor(color_func= settings.image_colors))
# plt.imshow(wc)
# plt.axis('off')
# plt.savefig('app/static/images/keywords.png')