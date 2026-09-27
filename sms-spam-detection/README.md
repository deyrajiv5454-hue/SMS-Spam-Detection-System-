# sms-spam-detection
Here is a complete guide to building your Flask application with user authentication and an SMS spam detection model.

We will break this project into three parts:
- __Training the Model:__ A script to parse your _spam.csv_ file, train a machine learning model, and save it.
- __The Flask Backend:__ The _app.py_ file that handles routing, database connections for authentication, and running predictions.
- __The Frontend Templates:__ The HTML files for login, registration, and user input.

## 1. Project Setup and Prerequisites
First, organize your project directory like this:
```
flask_spam_app/  
│  
├── spam.csv                 # Your training dataset  
├── train_model.py           # Script to train and save the model  
├── app.py                   # Main Flask application  
└── templates/               # Folder for HTML files  
   ├── layout.html  
   ├── login.html  
   ├── register.html  
   └── index.html  
```
Install the required Python libraries via your terminal:
> pip install Flask Flask-SQLAlchemy Flask-Login pandas scikit-learn werkzeug

## 2. Training the Model (train_model.py)
This script reads your _.csv_ data, trains a Naive Bayes classifier, and saves both the model and the vectorizer (which converts text to numbers) into _.pkl_ files so your Flask app can use them.

Assumes your _spam.csv_ has two columns: v1 (labels like "ham" or "spam") and v2 (the message text).

>Run this script once using python **train_model.py**. It will generate _model.pkl_ and _vectorizer.pkl_ in your project folder.

## 3. The Flask Application (app.py)
This file sets up a local SQLite database for users, manages user sessions via Flask-Login, and handles the POST request to predict spam.

## Final Steps
- Run python __app.py__ in your terminal.
- Open your browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).
- Register a new user, log in, and test some text messages!
