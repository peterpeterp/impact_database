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


from wtforms import RadioField, SelectMultipleField, TextField, IntegerField, SelectField, StringField
from flask.ext.wtf import Form, validators
from wtforms.validators import ValidationError, Required, Regexp



class RegionForm(Form):
  regions = SelectField(u'Available Regions', choices=[],
            validators=[Required("Please select at least one region.")])

class ThematicForm(Form):
  thematics = SelectField(u'Available Thematics', choices=[],
            validators=[Required("Please select at least one Thematic.")])

class TypeForm(Form):
  types = SelectField(u'Type of Study', choices=[],
            validators=[Required("Please select at least one Type of Study.")])

class SearchForm(Form):
  search = StringField(u'asdasd')

class UnsortedForm(Form):
  unsorteds = SelectField(u'', choices=[],
            validators=[Required("Please select at least one unsorted.")])

class SelectedForm(Form):
  selected = SelectField(u'Selected Keywords', choices=[],
            validators=[Required("Please select at least one keyword.")])
