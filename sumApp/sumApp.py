import base64
from bs4 import BeautifulSoup
import datetime
import docx2txt
from io import StringIO
import os
from PIL import Image
import PyPDF2
from pymongo import MongoClient
import re
import requests 
import ssl
import streamlit as st
import torch
import timeit
import urllib.request, urllib.parse, urllib.error
import config

st.set_page_config(page_title="sumApp", page_icon="🐞", layout="centered", initial_sidebar_state="auto", menu_items=None)

if not hasattr(st, "client"):
    st.client = MongoClient('mongodb://127.0.0.1/local')
collection = st.client.local.user

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def parse(ARTICLE):
    max_chunk = 500
    ARTICLE = ARTICLE.replace('.', '.<eos>')
    ARTICLE = ARTICLE.replace('?', '?<eos>')
    ARTICLE = ARTICLE.replace('!', '!<eos>')
    sentences = ARTICLE.split('<eos>')
    current_chunk = 0 
    chunks = []
    for sentence in sentences:
        if len(chunks) == current_chunk + 1: 
            if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                chunks[current_chunk].extend(sentence.split(' '))
            else:
                current_chunk += 1
                chunks.append(sentence.split(' '))
        else:
            chunks.append(sentence.split(' '))

    for chunk_id in range(len(chunks)):
        chunks[chunk_id] = ' '.join(chunks[chunk_id])

    st.write("Number of chunks:", len(chunks), ", summarize...")
    return ARTICLE

img = Image.open("hipushi.jpg")
st.image(img, width=70)
st.header("sumApp")
article = st.text_area('URL/Text to be summarized:', height=200)
if article == "" or len(article) <= 1:
    article = 'https://en.wikipedia.org/wiki/Hello_Kitty'

start_time=timeit.default_timer()
def end_timer(suffix = None):
    evalTime = timeit.default_timer() - start_time
    #suffix = "" if suffix is None else "_" + suffix
    #text = (str(evalTime))
    #with open('runtime.txt', 'w') as f:
     #   f.write(text)
    st.write("time: ",evalTime,'s')
    return evalTime

API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
headers = {"Authorization": config.api_key}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    text = docx2txt.process(uploaded_file)
    output_doc = query(text)
    st.write(output_doc)
    time = end_timer()
    collection.insert_one({'name': str(uploaded_file), 'summary': output_doc[0]['summary_text'], 'timer': time, 'date': datetime.datetime.now()})
    with open("my_file.txt", 'w') as my_data:
           my_data.write(str(output_doc[0]['summary_text']))
    st.markdown(get_binary_file_downloader_html('my_file.txt', 'summary'), unsafe_allow_html=True)

if st.button("Summarize"): 
    txt = article.strip()
    starturl = article.strip()
    if ( starturl.startswith('http') ) : 
        #Ignore SSL certificate errors
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        if ( starturl.endswith('.htm') or starturl.endswith('.html') ) :
            pos = starturl.rfind('/')
            web = starturl[:pos]

        try:
            #html = urllib.request.urlopen(starturl, context=ctx).read()
            document = urllib.request.urlopen(starturl, context=ctx)
            html = document.read()
            if document.getcode() != 200 :
                st.write("Error on page: ",document.getcode())
            
            #if 'text/html' != document.info().get_content_type() :
             #   st.write("Ignore non text/html page")

            st.write('Characters:('+str(len(html))+')', end=' ')
    
        except KeyboardInterrupt:
            st.write('')
            st.write('Program interrupted by user...')
    
        #except:
         #   st.write("Unable to retrieve or parse page")

        r = requests.get(starturl)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.find_all(['h1', 'p'])
        text = [result.text for result in results]
        ARTICLE = ' '.join(text)

        # Retrieve all of the title tags
        txt = list()
        title=""
        tags_second = soup('title')
        for name in tags_second:
            title=txt.append(name.get_text())
            #print(title)

        x = re.search("\w+$", starturl)
        if (starturl.endswith('pdf') or starturl.endswith(str(x))):
            #url = ''
            #response = requests.get(url)
            my_raw_data = r.content

            with open("my_pdf.pdf", 'wb') as my_data:
                my_data.write(my_raw_data)

            open_pdf_file = open("my_pdf.pdf", 'rb')
            read_pdf = PyPDF2.PdfReader(open_pdf_file)
            if read_pdf.is_encrypted:
                read_pdf.decrypt("")
                #print(read_pdf.pages[0].extract_text())
                ARTICLE = read_pdf.pages[0].extract_text()
            else:
                print(read_pdf.pages[0].extract_text())
                ARTICLE = read_pdf.pages[0].extract_text()

        ARTICLE = parse(ARTICLE)
###        
        output  = query(ARTICLE.strip())
        st.write(output)

        with open("my_file.txt", 'w') as my_data:
           my_data.write(str(output[0]['summary_text']))       

    else:
        txt = parse(article)
        starturl = article[:10]
        
#        
        output = query(txt)
        for value in output:
            #st.write(value["summary_text"])
            st.write(value)

        with open("my_file.txt", 'w') as my_data:
           my_data.write(str(output[0]['summary_text']))
        
    st.markdown(get_binary_file_downloader_html('my_file.txt', 'summary'), unsafe_allow_html=True)

    time = end_timer()
    if output:
            collection.insert_one({'name': starturl, 'summary': output[0]['summary_text'], 'timer': time, 'date': datetime.datetime.now()})
       
