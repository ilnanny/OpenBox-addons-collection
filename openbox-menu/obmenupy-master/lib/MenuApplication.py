import json
from lib.Cache import Cache
from xml.etree.ElementTree import Element, SubElement, tostring
from lib.Application import Application
from xdg import Config


class MenuApplication(Application):
    _config = {}
    _desktopEntryPaths = {}
    _menuObj = {}
    _cache = None

    def __init__(self, args):
        Application.__init__(self, args)
        paths = self.getConfigPaths()
        self._config = self.getConfigFiles(paths)
        self._menuObj = json.load(open(self._config['menu.cfg']))
        self._cache = Cache(self.getArg('homeConfigDir') + '/' + self.getArg('cacheDirSuffix'))
        self._initIconTheme(self.getArg('iconTheme'));

    def _initIconTheme(self, iconTheme = None):
        if not iconTheme is None:
            Config.setIconTheme(iconTheme)

    def run(self):
        menuRoot = Element("openbox_pipe_menu")
        self._itemsMake(menuRoot, self._menuObj)
        return tostring(menuRoot).decode()

    def _itemsMake(self, rootElem, cfgObject, elemId=None):
        if 'name' in cfgObject and cfgObject['name'] is not None:
            self._makeSeparatorItem(rootElem, cfgObject['name'])
        items = {}
        if type(cfgObject['items']) is dict:
            items = cfgObject['items']
        elif elemId is not None and elemId + '.cfg' in self._config:
            items = json.load(open(self._config[elemId + '.cfg']))
        elif cfgObject['exec'] is not None and type(cfgObject['exec']) is dict:
            moduleObj = __import__(cfgObject['exec']['module'], globals(), locals(), cfgObject['exec']['className'])
            classObj = getattr(moduleObj, cfgObject['exec']['className'])
            classInstance = classObj(self._cache, self._config)
            method = getattr(classInstance, cfgObject['exec']['methodName'])
            items = method()

        for itemId in sorted(items.keys()):
            item = items[itemId]
            methodName = '_' + item['type'] + 'Make'
            methodToExec = getattr(self, methodName)
            try:
                methodToExec(rootElem, item, itemId)
            except AttributeError:
                continue

    def _separatorMake(self, rootElem, cfgObject, elemId=None):
        name = cfgObject['name'] if 'name' in cfgObject else None
        self._makeSeparatorItem(rootElem, name)

    def _itemMake(self, rootElem, cfgObject, elemId=None):
        self._makeItem(rootElem, cfgObject['name'], cfgObject['exec'], cfgObject['icon'])

    def _menuMake(self, rootElem, cfgObject, elemId=None):
        menuElem = self._makeMenuItem(rootElem, elemId, cfgObject['name'], cfgObject['icon'])
        self._itemsMake(menuElem, {'name': None, 'items': cfgObject['items'], 'type': 'items'})

    def _makeItem(self, root, name, pathToExec, iconPath=None):
        itemElement = SubElement(root, 'item', {'label': name})
        if not iconPath is None:
            itemElement.set('icon', iconPath)
        actionElement = SubElement(itemElement, 'action', {'name': 'Execute'})
        executeElement = SubElement(actionElement, 'execute')
        executeElement.text = pathToExec

    def _makeMenuItems(self, root, appsList):
        for app in appsList:
            self._makeItem(root, app['name'], app['command'], app['icon'])

    def _makeSeparatorItem(self, root, text=None):
        separator = SubElement(root, 'separator')
        if not text is None:
            separator.set('label', text)

    def _makeMenuItem(self, rootElem, elemId, name, icon):
        attributes = {"id": elemId,"label": name}
        if icon:
            attributes["icon"] = icon
        return SubElement(rootElem, "menu", attributes)
