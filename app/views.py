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

from flask import Flask, jsonify, render_template, request




import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image


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
  print 'choices'

  # create a word cloud
  selected=settings.bib.filter({'keywords':session['selected_keywords']})
  
  word_count,word_list,freq=settings.bib.check_occurence_of_keyword(selected)

  form_region, form_thematic, form_type, form_unsorted, form_selected = update_keywords(freq.keys())

  wc = WordCloud(background_color="white", max_words=2000,
               stopwords=stopwords, max_font_size=40, random_state=42)#,mask=settings.world_mask

  # wc.generate_from_frequencies(word_count)
  wc.generate(' '.join(word_list))

  # fig = plt.figure(figsize=(20,10))
  # #plt.imshow(wc.recolor(color_func= settings.image_colors))
  plt.imshow(wc)
  plt.axis('off')
  plt.savefig('app/static/images/keywords.png')

  list_=[]
  for i in selected:
    list_.append(settings.bib._articles[i])

  context = {
    'selected':list_,
    'picture_source':'static/images/keywords.png?'+str(int(round(time.time()))),
    'form_region':form_region, 
    'form_thematic':form_thematic,
    'form_type':form_type,
    'form_unsorted':form_unsorted,
    'form_selected':form_selected
  }

  return render_template('fixed_choices.html',**context)

@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    print 4
    return jsonify(result=a + b)
    # return redirect(url_for('choices'))


def update_keywords(remaining_keywords):
  print 'update'
  start=time.time()
  #session['selected_keywords']=session['regions_chosen']+session['thematics_chosen']+session['types_chosen']+session['unsorteds_chosen']
  form_selected = forms.SelectedForm(request.form)
  form_selected.selected.choices = zip(session['selected_keywords'],session['selected_keywords'])

  selected=settings.bib.filter({'keywords':session['selected_keywords']})

  form_region = forms.RegionForm(request.form)
  tmp = regions[:]
  for region in regions:
    if (region not in remaining_keywords) | (region in session['selected_keywords']): 
      tmp.remove(region)
  form_region.regions.choices = zip(tmp,tmp)

  form_thematic = forms.ThematicForm(request.form)
  tmp = thematics[:]
  for thematic in thematics:
    if (thematic not in remaining_keywords) | (thematic in session['selected_keywords']): 
      tmp.remove(thematic)
  form_thematic.thematics.choices = zip(tmp,tmp)

  form_type = forms.TypeForm(request.form)
  tmp = types[:]
  for type in types:
    if (type not in remaining_keywords) | (type in session['selected_keywords']): 
      tmp.remove(type)
  form_type.types.choices = zip(tmp,tmp)

  form_unsorted = forms.UnsortedForm(request.form)
  tmp = unsorteds[:]
  for unsorted in unsorteds:
    if (unsorted not in remaining_keywords) | (unsorted in session['selected_keywords']): 
      tmp.remove(unsorted)
  form_unsorted.unsorteds.choices = zip(tmp,tmp)

  print time.time()-start
  return form_region, form_thematic, form_type, form_unsorted, form_selected


@app.route('/add_region',  methods=('POST', ))
def add_region():
  form_region = forms.RegionForm(request.form)
  session['selected_keywords']+=[form_region.regions.data]
  #update_keywords()
  return redirect(url_for('choices'))

@app.route('/add_thematic',  methods=('POST', ))
def add_thematic():
  form_thematic = forms.ThematicForm(request.form)
  session['selected_keywords']+=[form_thematic.thematics.data]
  #update_keywords()
  return redirect(url_for('choices'))

@app.route('/add_type',  methods=('POST', ))
def add_type():
  form_type = forms.TypeForm(request.form)
  session['selected_keywords']+=[form_type.types.data]
  #update_keywords()
  return redirect(url_for('choices'))

@app.route('/add_unsorted',  methods=('POST', ))
def add_unsorted():
  form_unsorted = forms.UnsortedForm(request.form)
  session['selected_keywords']+=[form_unsorted.unsorteds.data]
  #update_keywords()
  return redirect(url_for('choices'))

@app.route('/remove_keyword',  methods=("POST", ))
def remove_keyword():
  form_selected = forms.SelectedForm(request.form)
  tmp=session['selected_keywords'][:]
  tmp.remove(form_selected.selected.data)
  session['selected_keywords']=tmp
  #update_keywords()
  return redirect(url_for('choices'))

@app.route('/clear_all',  methods=("POST", ))
def clear_all():
  session['selected_keywords']=[]
  #update_keywords()
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


