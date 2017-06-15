import chardet
def _2uni(s):
    try:
        return unicode(s)
    except:
        try:
            return unicode(s, 'UTF-8')
        except UnicodeDecodeError:
            try:
                return unicode(s, 'GBK')
            except UnicodeDecodeError:
                guess = chardet.detect(s)
                try:
                    return unicode(s, guess["encoding"])
                except:
                    return ""

def _2utf8(s):
    return _2uni(s).encode('UTF-8')

def _2gbk(s):
    return _2uni(s).encode('GBK')

def dict2utf8(d):
    ret = dict()
    for k in d.keys():
        nk = k
        nv = d[k]
        if isinstance(k, basestring):
            nk = _2utf8(k)
        if isinstance(nv, basestring):
            ret[nk]=_2utf8(nv)
        elif isinstance(nv, list):
            ret[nk]=list2utf8(nv)
        elif isinstance(nv, dict):
            ret[nk]=dict2utf8(nv)
        else:
            ret[nk]=nv
    return ret
def list2utf8(l):
    ret = []
    for item in l:
        nv = item
        if isinstance(nv, basestring):
            ret.append(_2utf8(nv))
        elif isinstance(nv, list):
            ret.append(list2utf8(nv))
        elif isinstance(nv, dict):
            ret.append(dict2utf8(nv))
        else:
            ret.append(nv)
    return ret

import json
def save2json(d, pf):
    f = open(pf,'w')
    f.write(json.dumps(d, ensure_ascii=False, indent=4))
    f.close()

def json2load(pf):
    f = open(pf,'r')
    s = ''.join(f.readlines())
    d = json.loads(s)
    d = dict2utf8(d)
    f.close()
    return d

def invert_dict(d):
    return dict([(v,k) for k,v in d.iteritems()])


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
