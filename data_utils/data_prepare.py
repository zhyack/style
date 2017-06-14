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
    try:
        return unicode(s, guess["encoding"])
    except UnicodeDecodeError:
        try:
            return unicode(s, 'UTF-8')
        except UnicodeDecodeError:
            return unicode(s, 'GBK')
def _2utf8(s):
    return _2uni(s).encode('UTF-8')

def save2map(d, pf):
    f = open(pf,'w')
    for k in d.keys():
        f.write(_2utf8(k)+'\n')
        f.write(_2utf8(d[k])+'\n')
    f.close()
def map2load(pf):
    f = open(pf,'r')
    d = dict()
    k = None
    cnt = 0
    for s in f.readlines():
        if cnt%2==1:
            d[k]=s.strip()
        else:
            k = s.strip()
        cnt += 1
    f.close()
    return d

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
        return 4, None
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
    if dbook.has_key(bookname):
        return 5, None, None, None
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
    if len(dbook)%100==0:
        print 'Start Autosaving... No CTRL+C!!!'
        save2map(dlang, base_data_dir+'/lang.map')
        save2map(dauthor, base_data_dir+'/author.map')
        save2map(dbook, base_data_dir+'/book.map')
        print 'Autosave completed! --- %d'%(len(dbook))
        print len(dlang),max([-1]+dlang.values())
        print len(dauthor),max([-1]+dauthor.values())
        print len(dbook),max([-1]+dbook.values())
    return 0, bookname, language, author


def allDFix():
    global dlang, dauthor, dbook
    rdauthor = dict((v,k) for k,v in dauthor.iteritems())
    for lang in os.listdir(base_data_dir):
        if lang.endswith('.map'):
            continue
        for author in os.listdir(base_data_dir+'/'+lang):
            for book in os.listdir(base_data_dir+'/'+lang+'/'+author):
                if not (book.endswith('.txt')):
                    continue
                book = book[:-4]
                f = open(base_data_dir+'/'+lang+'/'+author+'/'+ book+'.txt')
                content = f.readlines()
                bookname, authorname, language = None, None, None
                for i in range(min(100,len(content))):
                    line = content[i]
                    if line.startswith('Title:'):
                        bookname = line[7:].strip().rstrip().replace('/','|')
                    elif line.startswith('Author:'):
                        authorname = line[7:].strip().rstrip().replace('/','|')
                    elif line.startswith('Language:'):
                        language = line[9:].strip().rstrip().replace('/','|')
                f.close()
                if bookname==None or author==None or language==None:
                    raise Exception("Ohhh....%s"(base_data_dir+'/'+lang+'/'+author+'/'+ book+'.txt'))
                language = _2utf8(language)
                authorname = _2utf8(authorname)
                bookname = _2utf8(bookname)
                dlang[language]=lang
                dbook[bookname]=book
                if not rdauthor.has_key(author):
                    dauthor[authorname] = author
                    rdauthor[author] = authorname
                if rdauthor[author] != authorname:
                    if not dauthor.has_key(authorname) or dauthor[authorname]==author:
                        i = 0
                        while(rdauthor.has_key('%05d'%i)):
                            i+=1
                        dauthor[authorname]='%05d'%i
                        rdauthor[dauthor[authorname]]=authorname
                        os.mkdir('%s/%s/%s'%(base_data_dir, dlang[language], dauthor[authorname]))
                    os.system('mv %s/%s/%s/%s.txt %s/%s/%s/%s.txt'%(base_data_dir, lang, author, book, base_data_dir, lang, dauthor[authorname], book))
    save2map(dlang, base_data_dir+'/lang.map')
    save2map(dauthor, base_data_dir+'/author.map')
    save2map(dbook, base_data_dir+'/book.map')



def getAllBook(start_id, end_id, log_path="../log_getData.txt", interval=0):
    global dlang, dauthor, dbook
    dlang, dauthor, dbook = dict(), dict(), dict()
    history_flist = os.listdir(base_data_dir)
    if ('lang.map' in history_flist):
        dlang = map2load(base_data_dir+'/lang.map')
    if ('author.map' in history_flist):
        dauthor = map2load(base_data_dir+'/author.map')
    if ('book.map' in history_flist):
        dbook = map2load(base_data_dir+'/book.map')

    # allDFix()

    rdbook = set(dbook.values())
    print len(dlang),max([-1]+dlang.values())
    print len(dauthor),max([-1]+dauthor.values())
    print len(dbook),max([-1]+dbook.values())
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
            message = 'Cannot access to the link of the book(%d)...'%(bookid)
            retry_list.append(str(bookid))
        elif (state == 4):
            message = 'No link of the book(%d)...'%(bookid)
            dbook['%05d'%bookid]='%05d'%bookid
        elif (state == 5):
            message = 'Got book(%d), but duplicated. Abandon...'%(bookid)
            dbook['%05d'%bookid]='%05d'%bookid
        else:
            message = 'What happened with book(%d)? %s'%(bookid, str(state))
        print message
        flog.write(message+'\n')
        time.sleep(interval)
    save2map(dlang, base_data_dir+'/lang.map')
    save2map(dauthor, base_data_dir+'/author.map')
    save2map(dbook, base_data_dir+'/book.map')
    print 'All Done!'
    print 'Later you may want to retry the following: '
    print retry_list
    flog.write('[%s]'%(','.join(retry_list)))
    flog.close()
    return retry_list
