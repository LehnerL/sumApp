from transformers import BertTokenizerFast, EncoderDecoderModel
import torch
from bs4 import BeautifulSoup
import ssl
import urllib.request, urllib.parse, urllib.error
import requests
import sqlite3
import timeit

_start_time=timeit.default_timer()
#print(_start_time)
def end_timer(suffix = None):
    evalTime = timeit.default_timer() - _start_time
    #suffix = "" if suffix is None else "_" + suffix
    print("time: ",evalTime)
    text = (str(evalTime))
    with open('runtime.txt', 'w') as f:
        f.write(text)

conn = sqlite3.connect('sumapp.sqlite')
cur = conn.cursor()

#Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

starturl = input('Enter web url or enter: ')
if ( len(starturl) < 1 ) : starturl = 'https://en.wikipedia.org/wiki/Portal:Speculative_fiction'
if ( starturl.endswith('/') ) : starturl = starturl[:-1]

html = urllib.request.urlopen(starturl, context=ctx).read()

#summarizer = pipeline("summarization")
#URL = "http://galactanet.com/oneoff/theegg_mod.html"
#URL = "https://en.wikipedia.org/wiki/Kawaii"

r = requests.get(starturl)
soup = BeautifulSoup(r.text, 'html.parser')
results = soup.find_all(['h1', 'p'])
text = [result.text for result in results]
ARTICLE = ' '.join(text)
#print(ARTICLE)

web = starturl
if ( starturl.endswith('.htm') or starturl.endswith('.html') ) :
    pos = starturl.rfind('/')
    web = starturl[:pos]

if ( len(web) > 1 ) :
    cur.execute('INSERT OR IGNORE INTO Websites (url) VALUES ( ? )', ( web, ) )
    cur.execute('INSERT OR IGNORE INTO Pages (url, html, new_rank) VALUES ( ?, ?, 1.0 )', ( starturl, html) )
    conn.commit()

try:
    document = urlopen(url, context=ctx)

    html = document.read()
    if document.getcode() != 200 :
        print("Error on page: ",document.getcode())
        cur.execute('UPDATE Pages SET error=? WHERE url=?', (document.getcode(), web) )

    if 'text/html' != document.info().get_content_type() :
        print("Ignore non text/html page")
        cur.execute('DELETE FROM Pages WHERE url=?', ( web, ) )
        conn.commit()
        

    print('('+str(len(html))+')', end=' ')

    
except KeyboardInterrupt:
    print('')
    print('Program interrupted by user...')
    
except:
    #print("Unable to retrieve or parse page")
    cur.execute('UPDATE Pages SET error=-1 WHERE url=?', (web, ) )
    conn.commit()

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
        #print(current_chunk)
        chunks.append(sentence.split(' '))

for chunk_id in range(len(chunks)):
    chunks[chunk_id] = ' '.join(chunks[chunk_id])

print("Number of chunks:", len(chunks), ",summarize..")

#res = summarizer(chunks, max_length=120, min_length=30, do_sample=False)
 
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = BertTokenizerFast.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization')
model = EncoderDecoderModel.from_pretrained('mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization').to(device)

def generate_summary(text):
    # cut off at BERT max length 512
    inputs = tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt")
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)

    output = model.generate(input_ids, attention_mask=attention_mask)
    
    return tokenizer.decode(output[0], skip_special_tokens=True)

#fname = input('Enter file name: ')
#if (len(fname) < 1): fname = 'romeo.txt' 
#txt = [
    #(open(fname)).read()
#   str(ARTICLE)

#]
sum = generate_summary(str(ARTICLE))
print(sum)

# Retrieve all of the title tags
txt = list()
tags_second = soup('title')
for title in tags_second:
    txt.append(title.get_text())
    #print(title.get_text())

cur.execute('INSERT OR IGNORE INTO urlIndexes (url, url_title, url_full_txt, url_sum) VALUES ( ?, ?, ?, ?)',
               ( (starturl, title.get_text().strip() ,str(ARTICLE).strip() , str(sum)) ) )

conn.commit()
cur.close()

end_timer()
