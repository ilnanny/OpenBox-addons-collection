import json
from os.path import isdir
from os import makedirs
from hashlib import md5


class Cache(object):
    _path = None

    def __init__(self, path):
        self._path = path
        if not isdir(path):
            makedirs(path, 0o750)

    def write(self, key, hashStr, data):
        fullPath = self._path + '/' + key
        data = {'hash': hashStr, 'content': data}
        json.dump(data, open(fullPath, 'w'))

    def read(self, key, hashStr):
        fullPath = self._path + '/' + key
        try:
            data = json.load(open(fullPath, 'r'))
            return data['content'] if data['hash'] == hashStr else {}
        except Exception as exc:
            return {}

    def makeHash(self, stringForHash):
        hashObj = md5(stringForHash.encode())
        hashStr = hashObj.hexdigest()
        return hashStr