import json
import re
from xdg import DesktopEntry, IconTheme, Config
from xdg.BaseDirectory import xdg_data_dirs
from os import path
from os import listdir


class ApplicationsList(object):
    _cache = None
    _ignoreList = None
    _categoryAliases = None
    _desktopEntryPaths = None
    _cacheKey = 'plugin.applications.list.json'

    def __init__(self, cache, config):
        """
        @type cache: lib.Cache.Cache
        """
        self._desktopEntryPaths = [pathPart + '/applications/'
                                   for pathPart in xdg_data_dirs
                                   if path.isdir(pathPart + '/applications/')]
        self._ignoreList = json.load(open(config['ignoreList.cfg'])) if 'ignoreList.cfg' in config else {}
        self._categoryAliases = json.load(
            open(config['categoryAliases.cfg'])) if 'categoryAliases.cfg' in config else {}
        self._cache = cache

    def make(self):
        fileList = self._getDesktopFileList(self._desktopEntryPaths)
        currentHash = ''.join(fileList)
        cachedData = self._cache.read(self._cacheKey, self._cache.makeHash(currentHash))
        if len(cachedData) > 0:
            return cachedData
        desktopExecRegExp = re.compile('(.+?)\s%.+')
        desktopEntriesInfo = [self._getItemInfo(desktopEntryPath, desktopExecRegExp)
                              for desktopEntryPath in fileList]
        menuObj = self._makeMenuCfg(desktopEntriesInfo)
        self._cache.write(self._cacheKey, self._cache.makeHash(currentHash), menuObj)
        return menuObj

    def _getDesktopFileList(self, paths):
        regexp = re.compile('.*?\.desktop$')
        desktopEntries = []
        for desktopEntriesPath in paths:
            desktopEntries += [desktopEntriesPath + desktopEntry for desktopEntry in listdir(desktopEntriesPath)
                               if re.match(regexp, desktopEntry)]
        return desktopEntries

    def _getItemInfo(self, desktopEntryPath, compiledRegexp):
        desktopEntry = DesktopEntry.DesktopEntry(desktopEntryPath)
        execCommand = desktopEntry.getExec()
        matchResult = re.match(compiledRegexp, execCommand)
        execCommand = execCommand if matchResult is None else matchResult.groups()[0]
        return {
            'categories': desktopEntry.getCategories(),
            'name': desktopEntry.getName(),
            'exec': execCommand,
            'iconPath': IconTheme.getIconPath(desktopEntry.getIcon(), 32, Config.icon_theme)
        }

    def _makeMenuCfg(self, entriesInformation):
        result = {}
        for entryInfo in entriesInformation:
            for category in entryInfo['categories']:
                if category not in self._ignoreList:
                    if category not in result:
                        result[category] = {
                            'name': self._categoryAliases[category] if category in self._categoryAliases else category,
                            'items': {},
                            'exec': None,
                            'icon': None,
                            'type': 'menu'
                        }
                    result[category]['items'][entryInfo['name']] = {
                        'name': entryInfo['name'],
                        'items': None,
                        'exec': entryInfo['exec'],
                        'icon': entryInfo['iconPath'],
                        'type': 'item'
                    }
        return result