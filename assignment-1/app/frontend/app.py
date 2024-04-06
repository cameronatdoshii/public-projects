import os
import requests
import logging
from flask import Flask, request, render_template, redirect, url_for, session, jsonify  
import boto3
from dynamo_helper import dynamo_helper
from s3_helper import s3_helper

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

dynamo_helper_instance = dynamo_helper()  

subscriptions = {
    "subbed_music": []
}

user = {
    "email": "",
    "user_name": "",
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        logger.info(f"Logging in with email: {email}")
        
        dynamo_helper_instance = dynamo_helper()
        success, message, user_name = dynamo_helper_instance.query_login(email, password, 'login')
        
        if success:
            user["email"] = email
            user["user_name"] = user_name
            session['logged_in'] = True  
            return redirect(url_for('main_page'))
        else:
            return render_template('login.html', error=message)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        user_name = request.form['user_name']
        password = request.form['password']

        dynamo_helper_instance = dynamo_helper()
        response = dynamo_helper_instance.add_user(email, user_name, password, 'login')

        if 'error' in response:
            return render_template('register.html', error=response['error'])
        else:
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/main')
def main_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    subscriptions["subbed_music"] = dynamo_helper_instance.get_subbed_music(user.get('email'))
    return render_template('main.html', user=user, subscriptions=subscriptions)

@app.route('/main-query-music', methods=['GET', 'POST'])
def main_query_music():
    if request.method == 'POST':
        logger.info("Querying music")
        dynamo_helper_instance = dynamo_helper()
        title = request.form.get('title', '')
        artist = request.form.get('artist', '')
        year = request.form.get('year', '')

        response = dynamo_helper_instance.query_music(title, artist, year)
        return jsonify(response)  # Send the response back as JSON
    else:
        return render_template('main.html')
    
@app.route('/main-music-subscribe', methods=['POST'])
def subscribe():
    logger.info("Subscribing to music")
    data = request.json
    email = user.get('email')
    subscriptions["subbed_music"].append({
        "Title": data.get('title'),
        "Artist": data.get('artist'),
        "Year": data.get('year'),
        "ImagePath": data.get('imagePath')
    })
    
    logger.info(f"Subscribed to {data.get('title')} by {data.get('artist')} released in {data.get('year')}")
    logger.info(subscriptions)
    logger.info(email)
    music = dynamo_helper_instance.add_subbed_music(subscriptions, email)
    subscriptions["subbed_music"] = music
    logger.info(f"Subscribed music: {music}")

    return jsonify({"message": "Subscription added"}), 200

@app.route('/generate-presigned-url', methods=['GET'])
def generate_presigned_url():
    logger.info("Generating presigned URL")
    bucket_name = 's3864826-a1-music-image-bucket'
    path = request.args.get('path')

    if not path:
        return jsonify({'error': 'Missing path parameter'}), 400

    expiration = 3600  
    
    s3_helper_instance = s3_helper()
    response = s3_helper_instance.generate_presigned_url(bucket_name, path, expiration)
    
    return jsonify({'url': response}), 200

@app.route('/remove-subscription', methods=['POST'])
def remove_subscription():
    logger.info("Removing subscription")
    data = request.json
    email = user.get('email')
    title = data.get('title')
    artist = data.get('artist')
    year = data.get('year')
    subscriptions["subbed_music"] = dynamo_helper_instance.remove_subbed_music(title, artist, year, email)
    logger.info(f"Removed subscription: {title} by {artist} released in {year}")
    logger.info(subscriptions)
    return jsonify({"message": "Subscription removed"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
