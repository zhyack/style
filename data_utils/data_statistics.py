import os

allf = dict()
rootp = ""
base_data_dir = "C:/Users/zhy-win/Desktop/vps/data"

def cntWords(p,d=0):
    global allf
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
    return ret_words

def cntSubs(p,d=0):
    global allf
    print p
    ret_folders, ret_files, ret_words = 0,0,0
    sublist = os.listdir(p)
    for subp in sublist:
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
    return ret_folders, ret_files, ret_words

def init(p=base_data_dir):
    global allf
    allf = dict()
    cntSubs(p)
    global rootp
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
        print maxp[i]
    if (len(maxp)>20):
        print 'And More(%s)...'%(len(maxp))
