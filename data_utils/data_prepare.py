import os
import socket
socket.setdefaulttimeout(1)
import urllib
import time

base_url = "http://www.gutenberg.org/files/"
base_data_dir = "../data"

def getPage(url):
    trycnt = 5
    while(trycnt>0):
        try:
            urllib.urlretrieve(url, 'tmp.html')
        except IOError:
            print "Detected when crawling %s, retry now..."%(url)
            time.sleep(2)
            trycnt -= 1
            continue
        break
    if trycnt==0:
        return 3, None
    ftmp = open('tmp.html','r')
    content = ftmp.readlines()
    return 0, content

def getBookPlainTextLink(url):
    trycnt = 5
    while(trycnt>0):
        try:
            urllib.urlretrieve(url, 'tmp_folder.html')
        except IOError:
            print "Detected when crawling %s, retry now..."%(url)
            time.sleep(2)
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
    if (bookname == None) or (author == None) or (language == None):
        return 1, None, None, None
    language_dirs = os.listdir(base_data_dir)
    if not(language in language_dirs):
        os.mkdir('%s/%s'%(base_data_dir, language))
    author_dirs = os.listdir('%s/%s'%(base_data_dir, language))
    if not(author in author_dirs):
        os.mkdir('%s/%s/%s'%(base_data_dir, language, author))
    ftarget = open('%s/%s/%s/%s.txt'%(base_data_dir, language, author, bookname), 'w')
    ftarget.writelines(content)
    ftarget.close()
    return 0, bookname, language, author


def getAllBook(start_id, end_id, log_path="../log_getData.txt", interval=0):
    flog = open(log_path, 'w')
    retry_list = []
    for bookid in range(start_id, end_id+1):
        state, bookname, language, author = getBook(bookid)
        message = ""
        if (state == 0):
            message = 'Successfully get book(%d) <$%s$> writen by author <$%s$> in language <$%s$> .'%(bookid, bookname, author, language)
        elif (state == 1):
            message = 'Got book(%d), but missing important part. Abandon...'%(bookid)
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
    print 'All Done!'
    print 'Later you may want to retry the following: '
    print retry_list
    flog.write('[%s]'%(','.join(retry_list)))
    flog.close()

getAllBook(0, 54866)
