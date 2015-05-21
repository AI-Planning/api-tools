
import httplib, urllib, json, os, re

URL = 'api.planning.domains'

def query(qs, offline=False):

    assert not offline, "Error: Offline mode is not supported currently."

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    params = urllib.urlencode({})
    conn = httplib.HTTPConnection(URL)
    conn.request("GET", qs, params, headers)
    response = conn.getresponse()

    data = json.loads(response.read())
    conn.close()

    return data

def get_collections(ipc = None):
    """Return the collections, optionally which are IPC or non-IPC"""
    res = query('/collections/')
    if res['error']:
        print "Error: %s" % data['message']
        return []
    else:
        if ipc is not None:
            return filter(lambda x: x['ipc'] == ipc, res['result'])
        else:
            return res['result']

def get_collection(cid):
    """Return the collection of a given id"""
    res = query("/collection/%d" % cid)
    if res['error']:
        print "Error: %s" % data['message']
        return []
    else:
        return res['result']

def get_domains(cid):
    """Return the set of domains for a given collection id"""
    res = query("/domains/%d" % cid)
    if res['error']:
        print "Error: %s" % data['message']
        return []
    else:
        return res['result']

def get_problems(did):
    """Return the set of problems for a given domain id"""
    res = query("/problems/%d" % did)
    if res['error']:
        print "Error: %s" % data['message']
        return []
    else:
        return res['result']
