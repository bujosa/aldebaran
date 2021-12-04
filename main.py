import os
import threading
from flask.helpers import flash
from google.cloud import pubsub_v1
from flask import Flask, render_template, redirect, url_for
from crawlers.meli_dom import maindom
from crawlers.meli_mex import mainmex
from webforms import FormMeli

credentials_path = './configuration.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

subscriber = pubsub_v1.SubscriberClient()
subscription_path = os.environ['SUBSCRIPTION_NAME']

# TODO: Create callback function for messages
streaming_pull_future = subscriber.subscribe(subscription_path, callback=maindom)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form-dom', methods=['GET', 'POST'])
def melidom():
    form = FormMeli()

    if form.validate_on_submit():
        if form.secret.data != os.environ['SECRET_KEY']:
            flash("Wrong Secret - Try Again!", "error")
        else:
            threading.Thread(target=maindom, args=[int(form.days.data)], daemon=True).start()
            return redirect(url_for('index'))       

    return render_template('meli.html', form=form)    

@app.route('/form-mex', methods=['GET', 'POST'])
def melimex():
    form = FormMeli()

    if form.validate_on_submit():
        if form.secret.data != os.environ['SECRET_KEY']:
            flash("Wrong Secret - Try Again!", "error")
        else:
            threading.Thread(target=mainmex, args=[int(form.days.data)], daemon=True).start()
            return redirect(url_for('index'))           
             
    return render_template('meli.html', form=form)   

