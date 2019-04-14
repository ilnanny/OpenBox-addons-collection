__author__ = 'xproger'
from os import path, environ, listdir
from re import compile, match


class Application(object):
    _defaultArgs = {
        'configDir': '/etc/obmenupy',
        'homeConfigDir': environ['HOME'] + '/.config/obmenupy',
        'cacheDirSuffix': 'cache',
        'iconTheme': None
    }
    baseDir = None
    _args = None
    _configList = None

    def __init__(self, args):
        regexp = compile('^-{1,2}.+?=.+?')
        self.baseDir = path.dirname(args[0])
        self._args = {arg.split('=')[0].strip('-'): arg.split('=')[1] for arg in args[1:] if match(regexp, arg)}

    def getArg(self, argName):
        if argName not in self._defaultArgs:
            return None
        if argName in self._args.keys():
            return self._args[argName]
        return self._defaultArgs[argName]

    def run(self):
        pass

    def getConfigPaths(self):
        result = []
        if path.isdir(self.getArg('configDir')):
            result.append(self.getArg('configDir'))
        if path.isdir(self.getArg('homeConfigDir')):
            result.append(self.getArg('homeConfigDir'))
        return result

    def getConfigFiles(self, configPaths):
        files = {}
        for configPath in configPaths:
            filesList = {filePath: configPath + '/' + filePath for filePath in listdir(configPath)}
            for key in filesList:
                files[key] = filesList[key]
        return files