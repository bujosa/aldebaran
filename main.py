import os
from flask.helpers import flash
from google.cloud import pubsub_v1
from flask import Flask, render_template, redirect, url_for
from extract_functions.meli import main
from webforms import FormMeli
from threading import Thread

credentials_path = './configuration.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

subscriber = pubsub_v1.SubscriberClient()
subscription_path = os.environ['SUBSCRIPTION_NAME']

streaming_pull_future = subscriber.subscribe(subscription_path, callback=main)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form-rd', methods=['GET', 'POST'])
async def meli():
    form = FormMeli()
    if form.validate_on_submit():
        if form.secret.data != os.environ['SECRET_KEY']:
            flash("Wrong Secret - Try Again!", "error")
            
        else:
            flash("Scrawling... Data will be available in a few hours", "message")

            thread = Thread(target=main(int(form.days.data)))
            thread.daemon = True
            thread.start()

            flash("Finish Scraping", "message")

            return redirect(url_for('index'))            
    return render_template('meli.html', form=form)    
        

