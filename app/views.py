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


from app import app
from flask import redirect, render_template, url_for, request, flash, get_flashed_messages, g, session
from collections import OrderedDict
from werkzeug.routing import BuildError
import settings
import forms
import numpy as np
import glob,os,sys,time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


stopwords = set(STOPWORDS)
stopwords.add("said")
world_mask=np.array(Image.open("world.png"))
image_colors = ImageColorGenerator(world_mask)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field: %s" % (
                getattr(form, field).label.text,
                error
            ))


keywords = sorted([x.lower() for x in settings.keywords])
regions = sorted([x.lower() for x in settings.regions])
thematics = sorted([x.lower() for x in settings.thematics])
types  = sorted([x.lower() for x in settings.types])
unsorteds  = sorted([x.lower() for x in settings.unsorteds])



@app.route('/')
def index():
  session['regions_chosen']   = []
  session['selected_keywords']= []
  session['regions_chosen']   = []
  session['thematics_chosen']   = []
  session['types_chosen']  = []
  session['unsorteds_chosen']   = []

  return redirect(url_for("choices"))

@app.route('/choices')
def choices():

  try:
    session['selected_keywords']=session['regions_chosen']+session['thematics_chosen']+session['types_chosen']+session['unsorteds_chosen']
    form_selected = forms.SelectedForm(request.form)
    form_selected.selected.choices = zip(session['selected_keywords'],session['selected_keywords'])

    selected=settings.bib.filter({'keywords':session['selected_keywords']})

    form_region = forms.RegionForm(request.form)
    tmp = regions[:]
    for region in regions:
      if (len(settings.bib.filter({'keywords':session['selected_keywords']+[region]}))==0) | (region in session['regions_chosen']): 
        tmp.remove(region)
    form_region.regions.choices = zip(tmp,tmp)

    form_thematic = forms.ThematicForm(request.form)
    tmp = thematics[:]
    for thematic in thematics:
      if (len(settings.bib.filter({'keywords':session['selected_keywords']+[thematic]}))==0) | (thematic in session['thematics_chosen']): 
        tmp.remove(thematic)
    form_thematic.thematics.choices = zip(tmp,tmp)

    form_type = forms.TypeForm(request.form)
    tmp = types[:]
    for type in types:
      if (len(settings.bib.filter({'keywords':session['selected_keywords']+[type]}))==0) | (type in session['types_chosen']): 
        tmp.remove(type)
    form_type.types.choices = zip(tmp,tmp)

    form_unsorted = forms.UnsortedForm(request.form)
    tmp = unsorteds[:]
    for unsorted in unsorteds:
      if (len(settings.bib.filter({'keywords':session['selected_keywords']+[unsorted]}))==0) | (unsorted in session['unsorteds_chosen']): 
        tmp.remove(unsorted)
    form_unsorted.unsorteds.choices = zip(tmp,tmp)

  except KeyError:
    return redirect(url_for('index'))

  # create a word cloud
  selected=settings.bib.filter({'keywords':session['selected_keywords']})
  
  word_count,word_list,freq=settings.bib.check_occurence_of_keyword(selected)
  wc = settings.WordCloud(background_color="white", max_words=2000,
               stopwords=settings.stopwords, max_font_size=40, random_state=42)#,mask=settings.world_mask

  # wc.generate_from_frequencies(word_count)
  wc.generate(' '.join(word_list))

  # fig = plt.figure(figsize=(20,10))
  # #plt.imshow(wc.recolor(color_func= settings.image_colors))
  plt.imshow(wc)
  plt.axis('off')
  plt.savefig('app/static/images/keywords.png')

  # new.write('<div class="span4">\n<IMG SRC="static/images/keywords.png?'+str(int(round(time.time())))+'" ALT="some asdatext" WIDTH=500 HEIGHT=400>\n</div>\n')#WIDTH=1000 HEIGHT=1000



  list_=[]
  for i in selected:
    list_.append(settings.bib._articles[i])

  return render_template('fixed_choices.html',selected=list_,form_region=form_region, form_thematic=form_thematic,form_type=form_type,form_unsorted=form_unsorted,form_selected=form_selected)


@app.route('/remove_keyword',  methods=("POST", ))
def remove_keyword():
  form_selected = forms.SelectedForm(request.form)
  #if form_selected.validate_on_submit():
  if True:
    tmp_region=session['regions_chosen']
    tmp_thematic=session['thematics_chosen']
    tmp_type=session['types_chosen']
    tmp_unsorted=session['unsorteds_chosen']
    for key in form_selected.selected.data:
      print key
      if key in regions:  
        tmp_region.remove(key)
      if key in thematics:  
        tmp_thematic.remove(key)
      if key in types:  
        tmp_type.remove(key)
      if key in unsorteds:  
        tmp_unsorted.remove(key)

    session['regions_chosen'] = tmp_region
    session['thematics_chosen'] = tmp_thematic
    session['types_chosen'] = tmp_type
    session['unsorteds_chosen'] = tmp_unsorted
  else:
    flash_errors(form_selected)

  return redirect(url_for('choices'))


@app.route('/add_region',  methods=('POST', ))
def add_region():
  form_region = forms.RegionForm(request.form)
  form_region.regions.choices = zip(regions,regions)

  if form_region.validate_on_submit():
    session['regions_chosen']+=form_region.regions.data
  else:
    flash_errors(form_region)
  return redirect(url_for('choices'))


@app.route('/add_thematic',  methods=('POST', ))
def add_thematic():
  form_thematic = forms.ThematicForm(request.form)
  form_thematic.thematics.choices = zip(thematics,thematics)
  if form_thematic.validate_on_submit():
    session['thematics_chosen']+=form_thematic.thematics.data
  else:
    flash_errors(form_thematic)
  return redirect(url_for('choices'))

@app.route('/add_type',  methods=('POST', ))
def add_type():
  form_type = forms.TypeForm(request.form)
  form_type.types.choices = zip(types,types)
  if form_type.validate_on_submit():
    session['types_chosen']+=form_type.types.data
  else:
    flash_errors(form_type)
  return redirect(url_for('choices'))

@app.route('/add_unsorted',  methods=('POST', ))
def add_unsorted():
  form_unsorted = forms.UnsortedForm(request.form)
  form_unsorted.unsorteds.choices = zip(unsorteds,unsorteds)
  if form_unsorted.validate_on_submit():
    session['unsorteds_chosen']+=form_unsorted.unsorteds.data
  else:
    flash_errors(form_unsorted)
  return redirect(url_for('choices'))


@app.route('/home',  methods=('GET', ))
def render_home():
  return redirect(url_for('index'))

@app.route('/about',  methods=('GET', ))
def render_about():
  return render_template('about.html')

@app.route('/contact',  methods=('GET', ))
def render_contact():
  return render_template('contact.html')

@app.route('/documentation',  methods=('GET', ))
def render_docu():
  return render_template('documentation.html')


