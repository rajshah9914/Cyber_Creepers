from flask import Flask
app = Flask(__name__)
import requests
from flask import render_template 
import os
from flask import url_for, redirect,request
import bs4
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import xlrd
import re
import shutil

def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    # close open handles
    converter.close()
    fake_file_handle.close()
    if text:
        return text

import re, string, unicodedata
import nltk
import contractions
import inflect
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer

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

# Att = ["Fire", "Weapon", "Intruder"]
# filefire = open('fire.txt', 'r')
# fileWeapon = open('weapon.txt', 'r')
# fileIntruder = open('intruder.txt', 'r')

@app.route('/') 
def homepage():
    return render_template("index.html") 

@app.route("/displaycandidates", methods=['GET', 'POST'])                     #####  4th task
def displaycandidates():
    try:
        pst=request.form['pst']
    except:
        pst=""
    locate="fields.xlsx"
    wb = xlrd.open_workbook(locate) 
    sheet = wb.sheet_by_index(0)
    print("Hello")
    val=""
    for i in range(sheet.nrows): 
        # print(sheet.cell_value(i, 0)) 
        if(sheet.cell_value(i, 0)==pst):

            # print(sheet.cell_value(i, 1))
            val=sheet.cell_value(i, 1)
            break

    loc="skills.xlsx"
    # pst="Data Science"
    wb = xlrd.open_workbook(loc) 
    l=[]
    sheet = wb.sheet_by_index(0)
    delimeters=" ",".",","
    for i in range(sheet.nrows): 
        # print(sheet.cell_value(i, 0)) 
        if(sheet.cell_value(i, 0)==pst):
            # print(sheet.cell_value(i, 1))
            ll=sheet.cell_value(i, 1)
            l=re.split(';|,| ',ll)
            break
    print(l)
    d=[]
    if val!="":
        resumes=os.listdir(val)
    else:
        resumes=[]
    print(resumes)
    for resume in resumes:
        print(resume)
        c=int(0)
        p=[]
        words = extract_text_from_pdf(str(val)+'/'+str(resume))
        for i in l:
            if(words.find(i)!=-1):
                c=c+1
                print(i)
        
        p.append(c)
        p.append(str(resume))
        d.append(p)
    d.sort()
    d=d[::-1]
    print(d)
    jsonlist=[]
    for i in range(0,min(5,len(d))):
        jsonlist.append(d[i][1])
    print(jsonlist)
    # return jsonlist
    return render_template("displaycandidates.html", data=jsonlist)

@app.route("/adminn", methods=['GET', 'POST'])                     
def adminn():
    jsonlist=[]
    values=['Engineering','Management','Marketing','Not-Selected','CA','CS']
    for val in values:
        resumes=os.listdir(val)
        for resume in resumes:
            p=[]
            p.append(val)
            p.append(resume)
            jsonlist.append(p)
    return render_template("displaycateg.html", data=jsonlist)

engg_dict=dict()
mkt_dict=dict()
mgmt_dict=dict()
ca_dict=dict()
cs_dict=dict()
ca_dict['chartered accountant']=1
cs_dict['company secretary']=1
mkt_dict['public speaking']=1
mkt_dict['marketing']=1
mkt_dict['business']=1
mkt_dict['economics']=1
mgmt_dict['mba']=1
mgmt_dict['accounting']=1
engg_dict['technolog']=1
engg_dict['technology']=1
engg_dict['tech']=1
engg_dict['engineer']=1
engg_dict['algorithms']=1
engg_dict['engineering']=1
engg_dict['analyst']=1
engg_dict['data structure']=1


@app.route("/handleUpload", methods=['POST'])                         ###task upload 1
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':            
            photo.save(os.path.join('SampleUploads', photo.filename))
            shutil.copy2('SampleUploads/'+str(photo.filename), 'static')
            words = extract_text_from_pdf(os.path.join('SampleUploads', photo.filename))
        else:
            print("Sorry")
    else:
        print("Not Uploaded")
    
    # words = nltk.word_tokenize(words)

    # words = normalize(words)
    #print(words)
    # words = ' '.join(map(str, words))
    print(words)
    words=words.lower()
    f=0
    for i in mgmt_dict:
        if words.find(i)!=-1:
            print("Management")
            print(i)
            shutil.copy2('SampleUploads/'+str(photo.filename), 'Management')
            # photo.save(os.path.join('Management', photo.filename))
            f=1
            break
    for i in engg_dict:
        if words.find(i)!=-1:
            print("Engineering")
            print(i)
            f=1
            shutil.copy2('SampleUploads/'+str(photo.filename), 'Engineering')
            # photo.save(os.path.join('Engineering', photo.filename))
            break
    for i in mkt_dict:
        if words.find(i)!=-1:
            print("Marketing")
            print(i)
            f=1
            shutil.copy2('SampleUploads/'+str(photo.filename), 'Marketing')
            # photo.save(os.path.join('Marketing', photo.filename))
            break
    for i in ca_dict:
        if words.find(i)!=-1:
            f=1
            print(i)
            shutil.copy2('SampleUploads/'+str(photo.filename), 'CA')
            # photo.save(os.path.join('CA', photo.filename))
            print("CA")
            break
    for i in cs_dict:
        if words.find(i)!=-1:
            f=1
            print(i)
            print("CS")
            shutil.copy2('SampleUploads/'+str(photo.filename), 'CS')
            # photo.save(os.path.join('CS', photo.filename))
            break
    if f==0:
        print("Umeed par duniya kayam hai..")
        shutil.copy2('SampleUploads/'+str(photo.filename), 'Not-Selected')
        # photo.save(os.path.join('Non-Selected', photo.filename))
    # return redirect(url_for('homepage'))
    jsonlist=[]
    values=['Engineering','Management','Marketing','Not-Selected','CA','CS']
    for val in values:
        resumes=os.listdir(val)
        for resume in resumes:
            p=[]
            p.append(val)
            p.append(resume)
            jsonlist.append(p)

    return render_template("index.html")

@app.route("/searchcandidates", methods=['GET','POST'])                    ###task 3
def searchcandidates():
    # return render_template("searchcandidate.html")
    posi=request.form['position']
    loc=request.form['location']      
    browser = webdriver.Chrome('chromedriver')
    browser.get('http://www.yahoo.com')
    sleep(5)
    assert 'Yahoo' in browser.title
    
    elem = browser.find_element_by_name('p') # find the search box
    urlll='site:linkedin.com/in/ AND'+ str(posi) +'AND' +str(loc)
    res = elem.send_keys(urlll + Keys.RETURN)
    
    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    linkElems = soup.select('a')
    # for link in linkElems:
    #     print(f'link: {link}')
    numOpen = len(linkElems)

    browser.get('http://www.yahoo.com')
    sleep(5)
    assert 'Yahoo' in browser.title
    
    elem = browser.find_element_by_name('p') # find the search box
    urlll='site:indeed.co.in/ AND'+ str(posi) +' AND ' +str(loc)
    res = elem.send_keys(urlll + Keys.RETURN)
    
    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    linkElemss = soup.select('a')
    # for link in linkElems:
    #     print(f'link: {link}')
    numOpens = len(linkElemss)
    browser.quit()
    jsonlist=[]
    # jsonlist.append(posi)
    # jsonlist.append(loc)
    for i in range(numOpen):
        st=str(linkElems[i].get('href'))
        if (st.find(".linkedin.com") != -1):
            print(st)
            jsonlist.append(st)
    for i in range(0,numOpens):
        st=str(linkElemss[i].get('href'))
        if (st.find(".indeed.co.in") != -1):
            print(st)
            jsonlist.append(st)
    print(jsonlist)
    
    # return jsonlist
    return render_template("displayscrap.html", data=jsonlist)
    # return redirect(url_for('homepage'))

@app.route("/displayfilters", methods=['GET', 'POST'])                     #####  2nd task
def displayfilters():
    try:
        pst=request.form['suggest']
    except:
        pst=" "
    # loc=request.form['location']  
    # pst="Data Science"
    val=''
    locate="skills.xlsx"
    wb = xlrd.open_workbook(locate) 
    sheet = wb.sheet_by_index(0)
    # print("Hello")
    for i in range(sheet.nrows): 
        # print(sheet.cell_value(i, 0)) 
        if(sheet.cell_value(i, 0)==pst):
            # print(sheet.cell_value(i, 1))
            val=sheet.cell_value(i, 1).split(",")
            break
    jsonlist=[]
    jsonlist.append(pst)
    for i in val:
        jsonlist.append(i)
    # jsonlist.append(val)
    return render_template('displayfilters.html',data=jsonlist)

@app.route("/sms",methods=['GET','POST'])
def sms():
    url = "https://www.fast2sms.com/dev/bulk"
    msg="Congratulations on being Shortlisted..Please give the following test to qualify for an online interview.."+str('https://devfolio.co/')
    querystring = {"authorization":"QCtro4wOnvHH9n2LX3a3kN6QB6qJ9kIbDBAS7wzPVAcrZUu10BkHPGlN2ti6","sender_id":"FSTSMS","message":msg,"language":"english","route":"p","numbers":"9834576425"}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    # return response.text
    return render_template("index.html")

@app.route("/displayedtesting")                     #####  4th task
def displayedtesting():
    try:
        pst=request.form['pst']
    except:
        pst=""
    locate="fields.xlsx"
    wb = xlrd.open_workbook(locate) 
    sheet = wb.sheet_by_index(0)
    print("Hello")
    val=""
    for i in range(sheet.nrows): 
        # print(sheet.cell_value(i, 0)) 
        if(sheet.cell_value(i, 0)==pst):

            # print(sheet.cell_value(i, 1))
            val=sheet.cell_value(i, 1)
            break

    loc="skills.xlsx"
    # pst="Data Science"
    wb = xlrd.open_workbook(loc) 
    l=[]
    sheet = wb.sheet_by_index(0)
    delimeters=" ",".",","
    for i in range(sheet.nrows): 
        # print(sheet.cell_value(i, 0)) 
        if(sheet.cell_value(i, 0)==pst):
            # print(sheet.cell_value(i, 1))
            ll=sheet.cell_value(i, 1)
            l=re.split(';|,| ',ll)
            break
    print(l)
    d=[]
    if val!="":
        resumes=os.listdir(val)
    else:
        resumes=[]
    print(resumes)
    for resume in resumes:
        print(resume)
        c=int(0)
        p=[]
        words = extract_text_from_pdf(str(val)+'/'+str(resume))
        for i in l:
            if(words.find(i)!=-1):
                c=c+1
                print(i)
        
        p.append(c)
        p.append(str(resume))
        d.append(p)
    d.sort()
    d=d[::-1]
    print(d)
    jsonlist=[]
    for i in range(0,min(5,len(d))):
        jsonlist.append(d[i][1])
    print(jsonlist)
    # return jsonlist
    return render_template("displayedrendering.html", data=jsonlist)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
