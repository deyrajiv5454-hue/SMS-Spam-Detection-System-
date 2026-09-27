import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import pickle

# 1. Load the dataset (adjust encoding if needed)
df = pd.read_csv('spam.csv', encoding='latin-1')
df = df[['v1', 'v2']]
df.columns = ['label', 'message']

# Convert labels to binary (0 for ham, 1 for spam)
df['label'] = df['label'].map({'ham': 0, 'spam': 1})

# 2. Extract features using Bag of Words
cv = CountVectorizer()
X = cv.fit_transform(df['message'])
y = df['label']

# 3. Train the Naive Bayes Model
clf = MultinomialNB()
clf.fit(X, y)

# 4. Save the model and vectorizer to disk
with open('model.pkl', 'wb') as model_file:
    pickle.dump(clf, model_file)
    
with open('vectorizer.pkl', 'wb') as vocab_file:
    pickle.dump(cv, vocab_file)

print("Model and vectorizer trained and saved successfully!")