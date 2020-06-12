from flask import Flask
app = Flask(__name__)
import requests
import geocoder
from playsound import playsound
from flask import render_template 


import pyaudio
import wave
from wordAnalyzer import detectFraud


import re, string, unicodedata
import nltk
import inflect
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
import speech_recognition as sr
from pydub import AudioSegment
from os import path
import xlrd
import warnings 
warnings.filterwarnings(action = 'ignore') 
import gensim 
from gensim.models import Word2Vec 
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        # print(word)
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words

def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems

def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

def normalize(words):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    words = stem_words(words)
    words = lemmatize_verbs(words)
    return words

@app.route('/') 
def homepage():
    return render_template("index.html") 


@app.route('/startrecording')
def startrecording():
    # sound="checkup_2.wav"
    r = sr.Recognizer()
    # with sr.AudioFile(sound) as source: 
    with sr.Microphone() as source:
        print('Ready...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)
        words=r.recognize_google(audio).lower()
        words = nltk.word_tokenize(words)
        print(words)
        # words = normalize(words)
        # print(words)
        l=tuple(words)
        l=list(words)
        words = ' '.join(map(str, words))
        # print(words)
        file1 = open("audio.txt","w")
        file1.write(words)
        file1.close()

        loc="words.xlsx"
        dangerousWordFile = xlrd.open_workbook(loc)
        # l=[]
        # file1 = open("audio.txt", "r") 
        # s = file1.read() 
        
        # # Replaces escape character with space 
        # f = s.replace("\n", " ") 
        
        # data = [] 
        
        # # iterate through each sentence in the file 
        # for i in sent_tokenize(f): 
        #     temp = [] 
            
        #     # tokenize the sentence into words 
        #     for j in word_tokenize(i): 
        #         temp.append(j.lower()) 
        
        #     data.append(temp)
        # l=words
        # print(words)
        sheet = dangerousWordFile.sheet_by_index(0)
        rows=sheet.nrows
        columns=sheet.ncols
        list_for_model=[]
        for i in range(sheet.nrows):
            for j in range(sheet.ncols):
                list_for_model.append(sheet.cell_value(i,j))
        # print(list_for_model)
        list_for_check=tuple(list_for_model)
        list_for_check=list(list_for_model)
        for i in l:
            list_for_model.append(i)
        model1 = gensim.models.Word2Vec([list_for_model], min_count = 1, size = 10000, window = 5) 
        # print(model1)
        print(list_for_check)
        print(list_for_model)
        # print(l)
        count = 0
        print(l)
        for k in l:
            if(k not in list_for_check):
                # print(k)
                fuzzylist=process.extract(k, list_for_check)
                for tuples in fuzzylist:
                    if(tuples[1]>85):
                        cosine_similarity=model1.similarity(k,tuples[0])
                        cosine_similarity*=100
                        if(cosine_similarity>75):
                            sheet.write(rows-1,ncols,tuples[0])
                            print("Added to excel..")
            else:
                print(k,"present")
                count=count+1
        if(count>=3):
            playsound('beep.mp3')
            return render_template("index.html")
        else:
            return render_template("no_fraud.html") 


@app.route("/sms",methods=['GET','POST'])
def sms():
    url = "https://www.fast2sms.com/dev/bulk"
    g = geocoder.ip('me')
    print(g.latlng)
    lat=g.latlng[0]
    longi=g.latlng[1]
    msg="Alert! A fraud call has taken place at locations with latitude and longitude:- "+str(lat)+" " + str(longi) +". Please investigate at the earliest.. Sensitive Info. Leaked.."
    querystring = {"authorization":"N1LPbXtuIo0nfQXcfP7VioJOwjgnYwy7hPWsFZqLJcscbiCxcRHvkmCsGZ7U","sender_id":"FSTSMS","message":msg,"language":"english","route":"p","numbers":"9082420875"}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return render_template("index.html")

# @app.route("/beep",methods=['GET','POST'])
# def beep():
#     playsound('beep.mp3')
#     return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0')