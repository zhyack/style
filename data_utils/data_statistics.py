import os

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

allf = dict()
rootp = ""
base_data_dir = "../data"
dlang, dauthor, dbook = None, None, None

def cntWords(p,d=0):
    global allf, dbook
    ret_words = 0
    f = open(p, 'r')
    for line in f.readlines():
        ret_words += len(line.split())
    allf[p] = dict()
    allf[p]['type']='file'
    allf[p]['folers']=0
    allf[p]['files']=1
    allf[p]['words']=ret_words
    allf[p]['depth']=d
    try:
        allf[p]['name']=dbook[p[p.rfind('/')+1:p.rfind('.')]]
    except KeyError:
        del allf[p]
        ret_words = 0
    return ret_words

def cntSubs(p,d=0):
    global allf, dlang, dauthor
    print p
    ret_folders, ret_files, ret_words = 0,0,0
    sublist = os.listdir(p)
    for subp in sublist:
        if subp.endswith('.json'):
            continue
        subp = p + '/' + subp
        if os.path.isfile(subp):
            word_cnt = cntWords(subp, d+1)
            ret_files += 1
            ret_words += word_cnt
        elif os.path.isdir(subp):
            folder_cnt, file_cnt, word_cnt = cntSubs(subp, d+1)
            ret_folders += folder_cnt + 1
            ret_files += file_cnt
            ret_words += word_cnt
    allf[p] = dict()
    allf[p]['folders']=ret_folders+1
    allf[p]['files']=ret_files
    allf[p]['words']=ret_words
    allf[p]['type']='folder'
    allf[p]['depth']=d
    try:
        if d==0:
            allf[p]['name']='All'
        elif d == 1:
            allf[p]['name']=dlang[p[p.rfind('/')+1:]]
        elif d == 2:
            allf[p]['name']=dauthor[p[p.rfind('/')+1:]]
    except KeyError:
        del allf[p]
        ret_folders=0
        ret_files=0
        ret_words=0
    return ret_folders, ret_files, ret_words

def init(p=base_data_dir, rebuild=False, banlist=[[],['Various', 'Anonymous'],[]]):
    global allf, dlang, dauthor, dbook, rootp
    dlang = json2load(base_data_dir+'/lang.json')
    dauthor = json2load(base_data_dir+'/author.json')
    dbook = json2load(base_data_dir+'/book.json')
    for k in banlist[0]:
        if dlang.has_key(k):
            del(dlang[k])
    for k in banlist[1]:
        if dauthor.has_key(k):
            del(dauthor[k])
    for k in banlist[2]:
        if dbook.has_key(k):
            del(dbook[k])
    dlang = dict([(v,k) for k,v in dlang.iteritems()])
    dauthor = dict([(v,k) for k,v in dauthor.iteritems()])
    dbook = dict([(v,k) for k,v in dbook.iteritems()])
    allf = dict()
    if 'statistics.json' in os.listdir(p) and not rebuild:
        allf = json2load(p+'/statistics.json')
    else:
        cntSubs(p)
        save2json(allf, p+'/statistics.json')
    rootp = p
    print 'Init done...'

def queryCnt(p=rootp, depth=0, folders=True, files=True, words=True):
    print '\n\nQuery: path=%s&depth=%d'%(p,depth)
    if not allf.has_key(p):
        print 'Not Found!'
        return
    cnt_folders, cnt_files, cnt_words = 0,0,0
    base_depth = allf[p]['depth']
    for sp in allf.keys():
        if sp.startswith(p) and allf[sp]['depth']==base_depth+depth:
            cnt_folders += allf[sp]['folders']
            cnt_files += allf[sp]['files']
            cnt_words += allf[sp]['words']
    if folders:
        print 'Folders: %d'%(cnt_folders)
    if files:
        print 'Files: %d'%(cnt_files)
    if words:
        print 'Words: %d'%(cnt_words)

def queryMax(p=rootp, depth=0, tp='folder', metric='files'):
    print '\n\nMaxOf: path=%s&depth=%d'%(p,depth)
    if not allf.has_key(p):
        print 'Not Found!'
        return
    if not(tp=='folder' or tp=='file'):
        print 'Wrong Type!'
        return
    if not(metric=='folders' or metric=='files' or metric=='words'):
        print 'Wrong Metric!'
        return
    maxm = 0
    maxp = []
    base_depth = allf[p]['depth']
    for sp in allf.keys():
        if sp.startswith(p) and allf[sp]['depth']==base_depth+depth and allf[sp]['type']==tp:
            if allf[sp][metric]>= maxm:
                if allf[sp][metric]==maxm:
                    maxp.append(sp)
                else:
                    maxp = [sp]
                    maxm=allf[sp][metric]
    print 'Max [%s] of [%ss] is %d'%(metric,tp,maxm)
    print 'Refer to:'
    for i in range(min(20,len(maxp))):
        print maxp[i]+' --- %s'%(allf[maxp[i]]['name'])
    if (len(maxp)>20):
        print 'And More(%s)...'%(len(maxp))
