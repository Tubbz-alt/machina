from wtforms import Form, SelectField, RadioField, TextAreaField, SelectMultipleField, validators, widgets
from wtforms.csrf.session import SessionCSRF
from flask import session

from machina import database
import os

class CSRFForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = os.getenv('CSRF_SECRET_KEY').encode() if os.getenv('CSRF_SECRET_KEY') else os.urandom(24)

        @property
        def csrf_context(self):
            return session

class Measures(CSRFForm):
    choice = RadioField('Algorithm Choice', choices=[(1, 'Algorithm 1'), (2, 'Algorithm 2')], coerce=int, validators=[validators.InputRequired(message="Please choose which Algorithm you think will perform better")])
    confidence = SelectField('Confidence', choices=[('', 'Confidence')] + [ (str(i), str(i)) for i in range(1,11) ], validators=[validators.InputRequired(message="Please choose how confident you are in your choice")])

class Survey(CSRFForm):
    education = SelectField('Education Level', choices=[
        ('', 'Please Select Education Level'),
        ('1', 'Less than a high school diploma'),
        ('2', 'High school degree or equivalent (e.g. GED)'),
        ('3', 'Some college, no degree'),
        ('4', 'Associate degree (e.g. AA, AS)'),
        ('5', 'Bachelor’s degree (e.g. BA, BS)'),
        ('6', 'Some master’s education'),
        ('7', 'Master’s degree (e.g. MA, MS, MEd)'),
        ('8', 'Some doctoral education'),
        ('9', 'Doctorate (e.g. PhD)'),
        ('10', 'Some professional education'),        
        ('11', 'Professional degree (e.g. MD, JD, DDS)')
    ], validators=[validators.InputRequired()])

    computer_knowledge = SelectField('Computer Knowledge', choices=[
        ('', 'Please Select Computer Knowledge'),
        ('1', 'None'),
        ('2', 'Completed a tutorial or workshop (either online or in-person)'),
        ('3', 'Some of an online course'),
        ('4', 'Completed an online course'),
        ('5', 'Completed multiple online courses'),
        ('6', 'Some of a university course'),
        ('7', 'Completed a university course'),
        ('8', 'Completed enough courses for a university major or minor'),
    ], validators=[validators.InputRequired()])


    computer_experience = SelectField('Computer Experience', choices=[
        ('', 'Please Select Computer Experience'),
        ('1', 'None'),
        ('2', 'Occasional part-time work'),
        ('3', 'Consistent part-time work'),
        ('4', 'Less than one year of full-time work'),
        ('5', '1-2 years of full-time work'),
        ('6', '2-4 years of full-time work'),
        ('7', '4-6 years of full-time work'),
        ('8', 'More than 6 years of full-time work'),
    ], validators=[validators.InputRequired()])

    data_knowledge = SelectField('Data Knowledge', choices=[
        ('', 'Please Select Data Analysis Knowledge'),
        ('1', 'None'),
        ('2', 'Completed a tutorial or workshop (either online or in-person)'),
        ('3', 'Some of an online course'),
        ('4', 'Completed an online course'),
        ('5', 'Completed multiple online courses'),
        ('6', 'Some of a university course'),
        ('7', 'Completed a university course'),
        ('8', 'Completed enough courses for a university major or minor'),
    ], validators=[validators.InputRequired()])

    data_experience = SelectField('Data Experience', choices=[
        ('', 'Please Select Data Analysis Experience'),
        ('1', 'None'),
        ('2', 'Occasional part-time work'),
        ('3', 'Consistent part-time work'),
        ('4', 'Less than one year of full-time work'),
        ('5', '1-2 years of full-time work'),
        ('6', '2-4 years of full-time work'),
        ('7', '4-6 years of full-time work'),
        ('8', 'More than 6 years of full-time work'),
    ], validators=[validators.InputRequired()])

    feedback = TextAreaField('Feedback', render_kw={"placeholder": "Do you have any other feedback, questions, or suggestions about the task itself? Were the task and instructions clear?"})