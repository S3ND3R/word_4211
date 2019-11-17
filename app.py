from flask import Flask, request, Response, render_template
import requests
import itertools
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask.json import jsonify
from wtforms.validators import Regexp, ValidationError
import re

class EqualTo(object):
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if(int(other.data)> 1 and len(field.data) > 0):
            if len(field.data) != int(other.data):
                d = {
                    'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                    'other_name': self.fieldname
                }
                message = self.message
                if message is None:
                    message = field.gettext('Pattern length must be equal to %(other_label)s')
                raise ValidationError(message % d)

class OneRequired(object):
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data is "":
            if other.data is "":
                d = {
                    'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                    'other_name': self.fieldname
                }
                message = self.message
                if message is None:
                    message = field.gettext('must be provided if %(other_label)s is empty')
                raise ValidationError(message % d)

class WordForm(FlaskForm):
    avail_letters = StringField("Letters",
    validators= [Regexp(r'^[a-z]*$', message="must contain letters only"), OneRequired('pattern')
    ])
    pattern = StringField("Pattern", validators= [EqualTo('word_ln'),
    OneRequired('avail_letters')
    ])
    submit = SubmitField("Go")
    word_ln = SelectField("Word Length",
        choices=[
            ("0", "None"),
            ("3", "Three"),
            ("4", "Four"),
            ("5", "Five"),
            ("6", "Six"),
            ("7", "Seven"),
            ("8", "Eight"),
            ("9", "Nine"),
            ("10", "Ten")])

csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "burn their boat"
csrf.init_app(app)

@app.route('/index')
def index():
    form = WordForm()
    return render_template("index.html", form=form, name="Warren Weber")

@app.route('/words', methods=['POST', 'GET'])
def letters_2_words():
    form = WordForm()
    if form.validate_on_submit():
        letters = form.avail_letters.data

        # word lenth input
        ln = form.word_ln.data

        # pattern input
        pat = re.compile(form.pattern.data)
    else:
        return render_template("index.html", form=form)

    #build a set of good words
    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    if ((int(ln) != 0) or (len(letters) < 1)):
        if(len(letters) < 1):
            for word in good_words:
                if(form.pattern.data):
                    if re.fullmatch(pat, word):
                        word_set.add(word)
        else:
            for word in itertools.permutations(letters,int(ln)):
                w = "".join(word)
                if w in good_words:
                    if(form.pattern.data):
                        if re.fullmatch(pat, w):
                            word_set.add(w)
                    else:
                        word_set.add(w)
    else:
        for l in range(3, len(letters)+1):
            for word in itertools.permutations(letters,l):
                w = "".join(word)
                if w in good_words:
                    if(form.pattern.data):
                        if re.fullmatch(pat, w):
                            word_set.add(w)
                    else:
                        word_set.add(w)
    word_set = sorted(word_set)
    return render_template('wordlist.html',
        wordlist=sorted(word_set, key = len),
        name="Warren Weber")

@app.route('/<word>')
def dic_proxy(word):
    my_key = '0fe27d9e-cf27-4f01-a1e8-11412282a5d9'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={my_key}'
    x = requests.get(url)
    return jsonify(x.json())
