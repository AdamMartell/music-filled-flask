#!/usr/bin/env python2

from flask import Flask, render_template
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

Application = Flask(__name__)

class NameForm(Form):
    name = TextField('name', validators=[DataRequired()])

@Application.route('/form', methods=['GET', 'POST'])
def hello():
    form = NameForm(csrf_enabled=False)

    if form.validate_on_submit():
        name = form.name.data
    else:
        name = 'Unknown'

    return render_template('name.html', form=form, name=name)

if __name__ == '__main__':
    Application.run(host='0.0.0.0', port=9456, debug=True)
