import streamlit as st
import pickle
import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()

# from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

model = pickle.load(open('model.pkl','rb'))

st.set_page_config(
     page_title="Mail Spam Classifie",
     page_icon="email.png"
 )
 
def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
            
    text = y[:]
    y.clear()
    
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
            
    text = y[:]
    y.clear()
    
    for i in text:
        y.append(ps.stem(i))
    return " ".join(y)

st.title("Email / SMS spam classifier")
input_sms = st.text_area("Enter Message")
if st.button("Predict"):
    transformed_text = transform_text(input_sms)

    result = model.predict([transformed_text])[0]
    if result == 1:
        st.header("Spam Messsage")
    else:
        st.header("Not Spam / Ham Message")

if st.button("Check Last mail"):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=1313)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        results1 = service.users().messages().list(userId='me',maxResults=1).execute()
        ids = results1.get('messages', [])
        for id in ids:
            id = str(id['id'])
            results2 = service.users().messages().get(userId='me', id=id).execute()
            messages = results2.get('snippet', [])
        input_sms = messages
        transformed_text = transform_text(input_sms)
        result = model.predict([transformed_text])[0]
        st.write(input_sms)
        if result == 1:
            st.header("Spam Messsage")
        else:
            st.header("Not Spam / Ham Message")

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if st.button("Check All Spam mail"):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=1313)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        results1 = service.users().messages().list(userId='me',maxResults=20).execute()
        ids = results1.get('messages', [])
        message = []
        for id in ids:
            id = str(id['id'])
            results2 = service.users().messages().get(userId='me', id=id).execute()
            messages = results2.get('snippet', [])
            message.append(messages)
        msg = []
        st.header("List of Spam Mail")
        for i in range(len(ids)):
            input_sms = message[i]
            transformed_text = transform_text(input_sms)
            result = model.predict([transformed_text])[0]
            
            if result == 1:
                st.write(input_sms)
                st.header("")
    except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')
