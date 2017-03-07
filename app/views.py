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
  session['image_type'] = 'keyword'
  session['id']=str(int(round(time.time())))
  session['update']=['keywords','image']

  return redirect(url_for("choices"))

@app.route('/choices')
def choices():
  try:
    # create a word cloud
    selected=settings.bib.filter({'keywords':session['selected_keywords']})
    form_selected = forms.SelectedForm(request.form)
    form_selected.selected.choices = zip(session['selected_keywords'],session['selected_keywords'])

    word_list,freqency,word_count=settings.bib.count_occurence_of_keyword(selected)

    form_region, form_thematic, form_type = update_keywords(freqency.keys())

    form_unsorted = update_unsorteds(freqency.keys())

    if 'image' in session['update']:
      wc = WordCloud(background_color="white", max_words=2000,
                   stopwords=stopwords, max_font_size=40, random_state=42)#,mask=settings.world_mask

      if session['image_type']=='keyword':
        wc.generate_from_frequencies(word_count)
      if session['image_type']=='author':
        ttmp,tttmp,word_count=settings.bib.count_occurence_of_author(selected)
        wc.generate_from_frequencies(word_count)  
      if session['image_type']=='institution':
        ttmp,tttmp,word_count=settings.bib.count_occurence_of_institution(selected)
        wc.generate_from_frequencies(word_count)
      if session['image_type']=='journal':
        ttmp,tttmp,word_count=settings.bib.count_occurence_of_journal(selected)
        wc.generate_from_frequencies(word_count)

      fig = plt.figure(figsize=(20,10))
      plt.imshow(wc)
      plt.axis('off')
      plt.savefig('app/static/images/keywords.png')

    list_=[]
    for i in selected:
      if settings.bib._articles[i].title!='':
        list_.append(settings.bib._articles[i])

    form_search=forms.SearchForm(request.form)
    form_search.search.data=session['search']

    context = {
      'selected':list_,
      'picture_source':'static/images/keywords.png?'+str(int(round(time.time()))),
      'bibtex_source':'../tmp/bibtex_'+session['id']+'.txt',
      'form_region':form_region, 
      'form_thematic':form_thematic,
      'form_type':form_type,
      'form_search':form_search,
      'form_unsorted':form_unsorted,
      'form_selected':form_selected,
    }

    session['update']=['keywords','image']

    return render_template('choices.html',**context)

  except:
   return redirect(url_for("index"))


@app.route('/export_bibtex',  methods=("GET", "POST", ))
def export_bibtex():
  print 'export'
  selected=settings.bib.filter({'keywords':session['selected_keywords']})

  list_=''
  for i in selected:
    if settings.bib._articles[i].title!='':
      list_+=settings.bib._articles[i].bibtex
      list_+='\n'


  return render_template('bibtex_export.html',selected=list_.split('\n'))

def update_unsorteds(remaining_keywords):
  form_unsorted = forms.UnsortedForm(request.form)
  tmp = unsorteds[:]
  for unsorted in unsorteds:
    if (unsorted not in remaining_keywords) | (unsorted in session['selected_keywords']) | (unsorted[:len(session['search'])]!=session['search']): 
      tmp.remove(unsorted)
  form_unsorted.unsorteds.choices = zip(tmp,tmp)

  return form_unsorted

def update_keywords(remaining_keywords):
  print 'update'
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

  return form_region, form_thematic, form_type

@app.route('/keyword_image',  methods=("GET", "POST", ))
def keyword_image():
  session['image_type']='keyword'
  return redirect(url_for('choices'))

@app.route('/author_image',  methods=("GET", "POST", ))
def author_image():
  print 'author'
  session['image_type']='author'
  return redirect(url_for('choices'))

@app.route('/institution_image',  methods=("GET", "POST", ))
def institution_image():
  session['image_type']='institution'
  return redirect(url_for('choices'))

@app.route('/journal_image',  methods=("GET", "POST", ))
def journal_image():
  session['image_type']='journal'
  return redirect(url_for('choices'))

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


