# coding: UTF-8
import os
import socket
socket.setdefaulttimeout(1)
import urllib
import time

import chardet
def _2uni(s):
    guess = chardet.detect(s)
    # if guess["confidence"] < 0.5:
    #     raise UnicodeDecodeError
    return unicode(s, guess["encoding"])
def _2utf8(s):
    return _2uni(s).encode('UTF-8')

import json
import yaml
def save2json(d, pf):
    f = open(pf,'w')
    f.write(json.dumps(d, ensure_ascii=False, indent=4))
    f.close()
def json2load(pf):
    f = open(pf,'r')
    s = ''.join(f.readlines())
    s = _2utf8(s)
    f.close()
    def custom_str_constructor(loader, node):
        return loader.construct_scalar(node).encode('utf-8')
    yaml.add_constructor(u'tag:yaml.org,2002:str', custom_str_constructor)
    return yaml.load(s)

base_url = "http://www.gutenberg.org/files/"
base_data_dir = "../data"
dlang, dauthor, dbook = None, None, None

def getPage(url):
    trycnt = 3
    while(trycnt>0):
        try:
            urllib.urlretrieve(url, 'tmp.html')
        except IOError:
            print "Detected when crawling %s, retry now..."%(url)
            time.sleep(1)
            trycnt -= 1
            continue
        break
    if trycnt==0:
        return 3, None
    ftmp = open('tmp.html','r')
    content = ftmp.readlines()
    return 0, content

def getBookPlainTextLink(url):
    trycnt = 3
    while(trycnt>0):
        try:
            urllib.urlretrieve(url, 'tmp_folder.html')
        except IOError:
            print "Detected when crawling %s, retry now..."%(url)
            time.sleep(1)
            trycnt -= 1
            continue
        break
    if trycnt==0:
        return 2, None
    ftmp = open('tmp_folder.html','r')
    l = ftmp.readlines()
    s = ''.join(l)

    p_link = ""
    en = s.find('/icons/text.gif')
    en = s.find('href=', en)
    en = s.find('>', en)
    st = en+1
    en = s.find('</a>',st)
    p_link = s[st:en]
    if len(p_link)<=4 or len(p_link)>=12:
        return 3, None
    return 0, url+'/'+p_link


def getBookPlainText(bookid):
    state, link = getBookPlainTextLink(base_url+str(bookid))
    if state != 0:
        return state, None
    state, content = getPage(link)
    if state != 0:
        return state, None
    return state, content

def getBook(bookid):
    global dlang, dauthor, dbook
    state, content = getBookPlainText(bookid)
    if (state!=0):
        return state, None, None, None
    bookname = None
    author = None
    language = None
    for i in range(min(100,len(content))):
        line = content[i]
        if line.startswith('Title:'):
            bookname = line[7:].strip().rstrip().replace('/','|')
        elif line.startswith('Author:'):
            author = line[7:].strip().rstrip().replace('/','|')
        elif line.startswith('Language:'):
            language = line[9:].strip().rstrip().replace('/','|')
    if (bookname == None or len(bookname)==0) or (author == None or len(author)==0) or (language == None or len(language)==0):
        return 1, None, None, None
    language = _2utf8(language)
    author = _2utf8(author)
    bookname = _2utf8(bookname)
    language_dirs = os.listdir(base_data_dir)
    if not(dlang.has_key(language)):
        dlang[language] = '%02d'%len(dlang)
    if not(dlang[language] in language_dirs):
        os.mkdir('%s/%s'%(base_data_dir, dlang[language]))
    author_dirs = os.listdir('%s/%s'%(base_data_dir, dlang[language]))
    if not(dauthor.has_key(author)):
        dauthor[author] = '%05d'%len(dauthor)
    if not(dauthor[author] in author_dirs):
        os.mkdir('%s/%s/%s'%(base_data_dir, dlang[language], dauthor[author]))
    dbook[bookname]='%05d'%bookid
    ftarget = open('%s/%s/%s/%s.txt'%(base_data_dir, dlang[language], dauthor[author], dbook[bookname]), 'w')
    ftarget.writelines(content)
    ftarget.close()
    if len(dbook)%10==0:
        save2json(dlang, base_data_dir+'/lang.json')
        save2json(dauthor, base_data_dir+'/author.json')
        save2json(dbook, base_data_dir+'/book.json')
        print 'Autosave completed!'
    return 0, bookname, language, author


def getAllBook(start_id, end_id, log_path="../log_getData.txt", interval=0):
    global dlang, dauthor, dbook
    dlang, dauthor, dbook = dict(), dict(), dict()
    history_flist = os.listdir(base_data_dir)
    if ('lang.json' in history_flist):
        dlang = json2load(base_data_dir+'/lang.json')
    if ('author.json' in history_flist):
        dauthor = json2load(base_data_dir+'/author.json')
    if ('book.json' in history_flist):
        dbook = json2load(base_data_dir+'/book.json')
    rdbook = set()
    for k in dbook.keys():
        rdbook.add(dbook[k])
    flog = open(log_path, 'w')
    retry_list = []
    for bookid in range(start_id, end_id+1):
        if ('%05d'%bookid) in rdbook:
            continue
        state, bookname, language, author = getBook(bookid)
        message = ""
        if (state == 0):
            message = 'Successfully get book(%d) <$%s$> writen by author <$%s$> in language <$%s$> .'%(bookid, bookname, author, language)
        elif (state == 1):
            message = 'Got book(%d), but missing important part. Abandon...'%(bookid)
            dbook['%05d'%bookid]='%05d'%bookid
        elif (state == 2):
            message = 'Cannot get any txt entry of the book(%d)...'%(bookid)
            retry_list.append(str(bookid))
        elif (state == 3):
            message = 'Cannot access to the link of book(%d)...'%(bookid)
            retry_list.append(str(bookid))
        else:
            message = 'What happened with book(%d)? %s'%(bookid, str(state))
        print message
        flog.write(message+'\n')
        time.sleep(interval)
    save2json(dlang, base_data_dir+'./lang.json')
    save2json(dauthor, base_data_dir+'./author.json')
    save2json(dbook, base_data_dir+'./book.json')
    print 'All Done!'
    print 'Later you may want to retry the following: '
    print retry_list
    flog.write('[%s]'%(','.join(retry_list)))
    flog.close()
