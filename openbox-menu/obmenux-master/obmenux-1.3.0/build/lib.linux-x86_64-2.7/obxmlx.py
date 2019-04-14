
'''obxmlx.py component of
   Openbox Menu Editor X 1.3.0  2015 by SDE

   based on
   Openbox Menu Editor 1.0 beta 
   Copyright 2005 Manuel Colmenero 

     This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
 
     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.
 
     You should have received a copy of the GNU General Public License
     along with this program; if not, write to the Free Software
     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


  ObMenux can be used as a module in python scripts, for example, to
  Generate dynamic menus (pipemenus)
'''

import xml.dom.minidom

class ObMenux:

	# Internal functions =============================================

	def _clear_ids(self):
		# must be done when an XML change may change the menu nodes or paths
		self.ids = None

	#     navigation functions (they don't change the XML)
	
	def _get_dom_menu(self, menuid,
	                  func=lambda hasExecuteAttr: not hasExecuteAttr):
		''' gets a menu node by id in the dom;
		    func passed should return True when properties of the menu are as
		    wanted; returns None if no menu found passes that filter
		    (default filter is only menus that are not pipe-menus or links)
		    (menu nodes that are links are not unique by id and never returned)
		'''
		m_pair = self._get_menu_path(menuid, func)
		return m_pair[0]

	# Openbox id rule: Menu known by an id is the first of that id that has a
	#   label, in a depth-first search of each menu that is known by an id and
	#   does not have an execute attribute.
	#   (summary of the effect of openbox/menu.c parse_menu)
	def _find_menus(self, parent, m, path):
		n = 0
		for item in parent.childNodes:
			if item.nodeName == "menu" and (item.hasAttribute("id") and
			  item.hasAttribute("label") and item.getAttribute("id") not in m):
				m[item.getAttribute("id")] = (item, path + (n,))
				if item.hasChildNodes() and not item.hasAttribute("execute"):
					self._find_menus(item, m, path + (n,))
			if item.nodeName in ("menu","separator","item"):
				n += 1
	
	def _menu_is_non_link(self, hasExecuteAttr):
		return True
		
	def _menu_is_pipe(self, hasExecuteAttr):
		return hasExecuteAttr

	def _get_dom_ref(self, menu, parent):
		''' returns a link or a pipe menu or an empty menu with the given id
		    from the parent menu
		    (Warning: unsafe to use for retrieving links, because several may
		    have the same id; here for legacy only) '''
		if parent is None: #BUGFIX was `if not parent` but id may be falsy
			parent = self.dom.documentElement
		for item in parent.childNodes:
			if item.nodeName == "menu":
				if not item.hasChildNodes():
					if item.getAttribute("id") == menu: return item

	def _get_by_path(self, path):
		menu = self.dom.documentElement
		for index in path:
			found = None
			count = 0
			for it in menu.childNodes:
				if it.nodeType == it.ELEMENT_NODE and it.nodeName in ('menu',
				           'separator', 'item'):
					if index == count:
						found = it
						break
					count += 1
			if found is None:
				return
			menu = found
		return menu

	def _get_menu_path(self, menuid,
	                   func=lambda hasExecuteAttr: not hasExecuteAttr):
		''' like _get_dom_menu except returns (node, path)
		    or (None, None) if not found
		'''
		if menuid is None:
			return (self.dom.documentElement, ())
		self._get_ids()
		if menuid in self.ids:
			m_pair = self.ids[menuid]
		else:
			return None, None
		if func(m_pair[0].hasAttribute("execute")):
			return m_pair
		else:
			return None, None
	
	# used in obmenux main
	def _get_ids(self):
		if self.ids is None:
			self.ids = {}
			self._find_menus(self.dom.documentElement, self.ids, ())
		return self.ids
	
	def _get_node_path(self, node, parent=None, path=None):
		''' gets the path in integers of any node;
		    returned as a tuple or None if ID not found '''
		if path is None: path = ()
		if node is None:
			return
		if parent is None:
			parent = self.dom.documentElement
		n = 0
		for item in parent.childNodes:
			if item == node:
				return path + (n,)
			if item.nodeName == "menu" and item.hasChildNodes():
				b = self._get_node_path(node, item, path + (n,))
				if b is not None: return b
			if item.nodeName in ("menu","separator","item"):
				n += 1
	
	def _get_dom_item(self,menu,num):
		''' Get an item of 'menu', given its number (order) '''
		item = self._get_dom_menu(menu)
		if not item:
			return
		i = 0
		for it in item.childNodes:
			if it.nodeType == it.ELEMENT_NODE:
				if it.nodeName in ("menu","separator","item"):
					if i == num: return it
					i += 1

	def _get_menu_len(self,menu):
		'''	Get the number of items of a menu (viewable items, not all tags) '''
		item = self._get_dom_menu(menu)
		if item is None:
			return
		return self._get_len_by_node(item)

	# used in obmenux main
	def _get_menu_len_by_path(self, path):
		item = self._get_by_path(path)
		if item is None:
			return
		return self._get_len_by_node(item)
	
	def _get_len_by_node(self, node):
		i = 0
		for it in node.childNodes:
			if it.nodeType == it.ELEMENT_NODE:
				if it.nodeName in ("menu","separator","item"):
					i += 1
		return i

	def _get_real_num(self, menu, num):
		''' Get "real" item number (counting comments, text, etc. in the XML)
		    Returns None when 0-based index num not found '''
		item = self._get_dom_menu(menu)
		if item is None:
			return
		return self._get_real_by_node(item, num)
	
	def _get_real_by_node(self, node, num):
		i = 0; n = 0
		for it in node.childNodes:
			if it.nodeType == it.ELEMENT_NODE:
				if it.nodeName in ("menu","separator","item"):
					if i == num: return n
					i += 1
			n += 1
	
	# -------------------
	# procedures that change the XML that will be written to file
	# return True if change made, otherwise False
	
	def _put_dom_item(self, menu, nodo, pos=None):
		''' Insert a node in the xml tree '''
		parent = self._get_dom_menu(menu)
		if not parent:
			return False		
		if pos == None or pos > self._get_menu_len(menu):
			parent.appendChild(nodo)
		elif pos >= 0:
			ant = self._get_dom_item(menu, pos)
			parent.insertBefore(nodo, ant)
		self._clear_ids()
		return True

	def _put_by_path(self, path, nodo):
		''' Insert a node in the xml tree '''
		parent = self._get_by_path(path[:-1])
		if not parent: return False
		pos = path[-1]	
		if pos > self._get_menu_len_by_path(path[:-1]):
			parent.appendChild(nodo)
		elif pos >= 0:
			ant = self._get_by_path(path)
			parent.insertBefore(nodo, ant)
		else: return False
		self._clear_ids()
		return True

	def _set_item_node_props(self, itm, label, action, exe):
		# this is only for setting the the first action name
		#    and the first execute/command element for an "execute" action
		#    or a name for an action that has no contents
		itm.setAttribute("label", label)
		for it in itm.childNodes:
			if it.nodeType == it.ELEMENT_NODE and it.nodeName == "action":
				it.setAttribute("name", action)
				if action.lower() == "execute": #action name is case insensitive
					if it.childNodes is not None:
						for i in it.childNodes:
							if i.nodeType == i.ELEMENT_NODE and (i.nodeName ==
							           "execute" or i.nodeName == "command"):
								for item in i.childNodes:
									if item.nodeType == item.TEXT_NODE:
										item.nodeValue = exe
										return True
								txt = xml.dom.minidom.Text()
								txt.nodeValue = exe
								i.appendChild(txt)
								return True
					elm = xml.dom.minidom.Element("command")
					txt = xml.dom.minidom.Text()
					txt.nodeValue = exe
					elm.appendChild(txt)
					it.appendChild(elm)
					return True
				else:
					i = it.lastChild
					while i is not None:
						tmp = i.previousSibling
						it.removeChild(i)
						i.unlink()
						i = tmp
					return True
		it = xml.dom.minidom.Element("action")
		it.setAttribute("name", action)
		if action.lower() == "execute":
			elm = xml.dom.minidom.Element("command")
			txt = xml.dom.minidom.Text()
			txt.nodeValue = exe
			elm.appendChild(txt)
			it.appendChild(elm)
		itm.appendChild(it)
		return True

	# --------------------
	
	def _get_item_props(self,node):
		''' get the properties of an item from the xml, and returns them as a
		    dictionary. '''
		etiqueta = ""
		accion = ""
		param = ""
		icono = ""
		if node.hasAttribute("label"):
			etiqueta = node.getAttribute("label")
		if node.hasAttribute("icon"):
			icono = node.getAttribute("icon")
		for it in node.childNodes:
			if it.nodeType == it.ELEMENT_NODE and it.nodeName == "action":
				accion = it.getAttribute("name")
				if accion.lower() == "execute":
					for itm in it.childNodes:
						if itm.nodeType == itm.ELEMENT_NODE and (itm.nodeName
						            == "command" or itm.nodeName == "execute"):
							for item in itm.childNodes:
								if item.nodeType == item.TEXT_NODE:
									param = item.nodeValue.strip()
									break # first found text is the one to use
							break # use first found command or execute tag
		props = { "type": "item", "label": etiqueta, "action": accion,
		         "execute": param }
		if icono != "": props["icon"] = icono
		return props

	def _get_menu_props(self, node):
		'''	get the properties of a menu from the xml, and returns them as a
		    dictionary. '''
		mid = None; lb = None; ex = None; ico = None
		mnu = None; act = ""
		if node.hasAttribute("id"):
			mid = node.getAttribute("id")
		if node.hasAttribute("label"):
			lb = node.getAttribute("label")
		if node.hasAttribute("execute"):
			ex = node.getAttribute("execute")
		if node.hasAttribute("icon"):
			ico = node.getAttribute("icon")		
		if mid is None:
			act = "Hide" # one of the effects an Openbox menu tag can have
		else:
			mnu, m_pth = self._get_menu_path(mid, self._menu_is_non_link)
			if mnu is not None:
				if (m_pth < self._get_node_path(node)):
					act = "Link" # Openbox code says it must be a link. 
					if mnu.hasAttribute("label"):
						lb = mnu.getAttribute("label")
					else:
						lb = "[editor error: link to unlabeled menu]"
			if ex is not None and act != "Link":			
				act = "Pipemenu"
			if act != "Link" and lb is None and not node.hasChildNodes():
				act = "Link" # broken link, give fake label for warn/error
				lb2 = None if mnu is None else mnu.getAttribute("label")
				lb = self.idNotFoundMessage(mid, mnu is None, lb2)
		props = { "type": "menu", "action": act }
		if mid is not None: props["id"] = mid
		if lb is not None: props["label"] = lb
		if ex is not None: props["execute"] = ex
		if ico is not None: props["icon"] = ico
		return props

	def _get_sep_props(self,node):
		''' get the properties of a separator from the xml, and returns them as
		    a dictionary. '''
		if node.hasAttribute("label"):
			return { "type": "separator",
			         "label": node.getAttribute("label") }
		else:
			return { "type": "separator" }
	
	def _get_menu_by_node(self, menuid, node):
		lst = []
		if node is None:
			return lst
		for i in node.childNodes:
			if i.nodeType == i.ELEMENT_NODE:
				if i.nodeName == "menu":
					d = self._get_menu_props(i)
				elif i.nodeName == "separator":
					d = self._get_sep_props(i)
				elif i.nodeName == "item":
					d = self._get_item_props(i)
				else:
					continue
				d["parent"] = menuid
				lst.append(d)
		return lst
	
	#      functions that create nodes (not including placing them in the XML)
	
	def _create_item_node(self, label, action, execute):
		nodo = self.dom.createElement("item")
		nodo.setAttribute("label", label)
		accion = self.dom.createElement("action")
		accion.setAttribute("name", "Execute")
		exe = self.dom.createElement("command")
		txt = self.dom.createTextNode("")
		txt.nodeValue = execute
		exe.appendChild(txt)
		accion.appendChild(exe)
		nodo.appendChild(accion)
		return nodo

	def _create_link_node(self, mid):
		nodo = self.dom.createElement("menu")
		nodo.setAttribute("id", mid)
		return nodo

	def _create_menu_node(self, label, mid):
		nodo = self.dom.createElement("menu")
		nodo.setAttribute("label", label)
		nodo.setAttribute("id", mid)
		return nodo

	def _create_pipe_node(self, mid, label, execute):
		nodo = self.dom.createElement("menu")
		nodo.setAttribute("id", mid)
		nodo.setAttribute("label", label)
		nodo.setAttribute("execute", execute)
		return nodo

	def _create_sep_node(self, label=None):
		nodo = self.dom.createElement("separator")
		if label is not None:
			nodo.setAttribute("label", label)
		return nodo

	# Package level functions: ============================================

	#     used here and by obmenux
	
	def idNotFoundMessage(self, mid, absent=False, label=None):
		''' returns message for menu editor to show in place of a linked label
		    when Openbox would not recognize the link and not show it '''
		if absent: loc = 'at all'
		else: loc = 'above'
		if label is None or absent:
			return "[id '"+str(mid)+"' not found "+loc+"]"
		else:
			return "['"+str(label)+"' not found "+loc+"]"

	#     for use by obmenux

	def removeItemByPath(self, path):
		dom_mnu = self._get_by_path(path[:-1])
		if dom_mnu is None:
			return False
		item = self._get_by_path(path)
		if item is None:
			return False
		dom_mnu.removeChild(item)
		item.unlink()
		self._clear_ids()
		return True

	def removeMenuByPath(self, path):
		dom_mnu = self._get_by_path(path)
		if dom_mnu is None:
			return False
		if not dom_mnu.parentNode:
			self.dom.documentElement.removeChild(dom_mnu)
		else:
			dom_mnu.parentNode.removeChild(dom_mnu)
		dom_mnu.unlink()
		self._clear_ids()
		return True

	def createSepByPath(self, path, label=None):	
		nodo = self._create_sep_node(label)
		self._put_by_path(path, nodo)

	def createItemByPath(self, path, label, action, execute):
		nodo = self._create_item_node(label, action, execute)
		self._put_by_path(path, nodo)

	def createLinkByPath(self, path, mid):
		nodo = self._create_link_node(mid)
		self._put_by_path(path, nodo)
	
	def createPipeByPath(self, path, mid, label, execute):
		nodo = self._create_pipe_node(mid, label, execute)
		self._put_by_path(path, nodo)

	def createMenuByPath(self, path, label, mid):
		nodo = self._create_menu_node(label, mid)
		self._put_by_path(path, nodo)

	def interchangeByPath(self, path, n1, n2):
		dom_mnu = self._get_by_path(path)
		if dom_mnu is None:
			return False
		i1 = self._get_real_by_node(dom_mnu, n1)
		i2 = self._get_real_by_node(dom_mnu, n2)
		if i1 is None or i2 is None:
			return False
		tmp1 = dom_mnu.childNodes[i1].cloneNode(deep=True)
		tmp2 = dom_mnu.childNodes[i2].cloneNode(deep=True)
		dom_mnu.replaceChild(tmp2, dom_mnu.childNodes[i1])
		dom_mnu.replaceChild(tmp1, dom_mnu.childNodes[i2])
		self._clear_ids()
		return True

	def jumpMoveByPath(self, src_path, dest_path):
		smp = src_path[:-1]; dmp = dest_path[:-1]
		n1 = src_path[-1]; n2 = dest_path[-1]
		dom_mnu1 = self._get_by_path(smp)
		if dom_mnu1 is None:
			print ("invalid src menu path "+str(smp))
			return False
		dom_mnu2 = self._get_by_path(dmp)
		if dom_mnu2 is None:
			print ("invalid dmp menu path "+str(dmp))
			return False
		i1 = self._get_real_by_node(dom_mnu1, n1)
		if i1 is None:
			print ("n1 "+str(n1)+"  i1 "+str(i1))
			return False
		tmp = dom_mnu1.childNodes[i1].cloneNode(deep=True)
		dum = dom_mnu1.removeChild(dom_mnu1.childNodes[i1])
		dum.unlink() # should be unlinked if not used according to docs
		if smp == dmp and n1 < n2:
		    n2 -= 1
		i2 = self._get_real_by_node(dom_mnu2, n2)
		if i2 is None:
			dom_mnu2.insertBefore(tmp, None)
		else:
			dom_mnu2.insertBefore(tmp, dom_mnu2.childNodes[i2])
		self._clear_ids()
		return True

	def setItemPropsByPath(self, path, label, action, exe):
		itm = self._get_by_path(path)
		self._set_item_node_props(itm, label, action, exe)

	def getNonLinkLabel(self, mid, path):
		''' returns label for the menuid if exists before the tuple path '''
		mnu, m_pth = self._get_menu_path(mid, self._menu_is_non_link)
		if mnu is not None and m_pth < path:
			return mnu.getAttribute("label")		

	def getAttrByPath(self, path, attr):
		itm = self._get_by_path(path)
		if itm is not None and itm.hasAttribute(attr):
			return itm.getAttribute(attr)

	def setAttrByPath(self, path, attr, value=None):
		''' sets the attribute attr for the menu/item/separator at path
		    to the string value, removes the attribute if value is omitted;
		    True if changes dom, otherwise False '''
		itm = self._get_by_path(path)
		if itm is not None:
			if value is None:
				if itm.hasAttribute(attr):
					itm.removeAttribute(attr)
					self._clear_ids()
					return True
			else:
				if itm.hasAttribute(attr) and itm.getAttribute(attr) == value:
					return False
				itm.setAttribute(attr, value)
				self._clear_ids()
				return True
		return False
	
	def getMenuByPath(self,menuid,path):
		mnu = self._get_by_path(path)
		return self._get_menu_by_node(menuid, mnu)
	
	# Public functions ===================================================
	# Most of them are self-explanatory
				
	def loadMenu(self, filename):
		''' opens and closes filename; returns None when successful,
			otherwise "open for reading failed" or "parsing failed"
		    sets a model of the XML the file contains for this class to edit '''
		message = None
		try:
			fil = open(filename)
			try:
				self.dom = xml.dom.minidom.parseString(fil.read())
			except:
				message = "XML parsing failed"
				print(message+", filename: "+filename)
			fil.close()
		except:
			message = "open for reading failed"
			print(message+", filename: "+filename)
		self._clear_ids()
		return message
	
	def newMenu(self):
		''' sets the current model to an empty Openbox menu '''
		self.dom = xml.dom.minidom.parseString(
		"<?xml version=\"1.0\" ?><openbox_menu></openbox_menu>")
		self._clear_ids()

	def newPipe(self):
		''' sets the current model to an empty Openbox pipe menu '''
		self.dom = xml.dom.minidom.parseString(
		"<?xml version=\"1.0\" ?><openbox_pipe_menu></openbox_pipe_menu>")
		self._clear_ids()
	
	def saveMenu(self, filename):
		''' saves the current model as XML; 
		    returns None when successful, "writing failed" if unsuccessful '''
		message = None
		try:
			output = open(filename, "w")
			for line in self.dom.toprettyxml("\t","\n","utf-8").splitlines():
				if line.strip() != "":
					output.write("%s\n" %(line))
			output.close()
		except:
			message = "writing failed"
			print(message+", filename: "+filename)
		return message
	
	def printXml(self):
		''' prints the current model to stdout as XML '''
		for line in self.dom.toprettyxml("\t","\n","utf-8").splitlines():
			if line.strip() != "":
				print(line)
	
	def getXml(self):
		''' returns a string containing XML formed from the current model '''
		res = ""
		for line in self.dom.toprettyxml("\t","\n","utf-8").splitlines():
			if line.strip() != "":
				res = res + "%s\n" % (line)
		return res

	# Warning: all functions using "menu" parameter must only be called when
	#     every menu with contents in the document has a unique id and a label     

	def removeItem(self, menu, num):
		''' removes from menu (by ID) item num (0-based index) True if done '''
		dom_mnu = self._get_dom_menu(menu)
		if dom_mnu is None:
			return False
		item = self._get_dom_item(menu,num)
		if item is None:
			return False
		dom_mnu.removeChild(item)
		item.unlink()
		self._clear_ids()
		return True

	def removeMenu(self, menu):
		''' removes menu (by ID) for removing Menu or Pipemenu, not Link
		    True if successful '''
		dom_mnu = self._get_dom_menu(menu, func=self._menu_is_non_link)
		if dom_mnu is None:
			return False
		if not dom_mnu.parentNode:
			self.dom.documentElement.removeChild(dom_mnu)
		else:
			dom_mnu.parentNode.removeChild(dom_mnu)
		dom_mnu.unlink()
		self._clear_ids()
		return True

	def createSep(self, menu, pos=None, label=None):
		''' creates a Separator element in menu (by ID) at pos (0-based index) '''		
		nodo = self._create_sep_node(label)
		self._put_dom_item(menu, nodo, pos)
	
	def createItem(self, menu, label, action, execute, pos=None):
		''' Creates an item tag in menu (by ID) at pos (0-based index).
		    String label is assigned to the label attribute of the item tag.
		    An action tag is inserted and its name is set to "Execute".
		    The action argument is ignored.
		    String execute is inserted into a command tag. (Literal execute tags
		    are deprecated, though still recognized by obmenux.) '''
		nodo = self._create_item_node(label, action, execute)
		self._put_dom_item(menu, nodo, pos)

	def createLink(self, menu, mid, pos=None):
		''' at menu and pos
		    creates a menu item that has a menu ID string mid '''
		nodo = self._create_link_node(mid)
		self._put_dom_item(menu, nodo, pos)

	def createPipe(self, menu, mid, label, execute, pos=None):
		''' at menu and pos (or append if pos=None)
		    creates a menu item that has the specified id, label, and execute
		    attributes, and no child nodes '''
		nodo = self._create_pipe_node(mid, label, execute)
		self._put_dom_item(menu, nodo, pos)

	def createMenu(self, menu, label, mid, pos=None):
		''' at menu (by ID) and pos (DOM int)
		    creates a menu that has the specified label and id as attributes '''
		nodo = self._create_menu_node(label, mid)
		self._put_dom_item(menu, nodo, pos)

	def interchange(self, menu, n1, n2):
		''' within menu (by ID) swaps nodes n1 and n2
		    where n1 and n2 are integers representing tags in the menu
		    by a 0-based count (not all DOM nodes in the menu)
		    True when successful '''
		dom_mnu = self._get_dom_menu(menu)
		if dom_mnu is None:
			return False
		i1 = self._get_real_num(menu, n1)
		i2 = self._get_real_num(menu, n2)
		if i1 is None or i2 is None:
			return False
		tmp1 = dom_mnu.childNodes[i1].cloneNode(deep=True)
		tmp2 = dom_mnu.childNodes[i2].cloneNode(deep=True)
		dom_mnu.replaceChild(tmp2, dom_mnu.childNodes[i1])
		dom_mnu.replaceChild(tmp1, dom_mnu.childNodes[i2])
		self._clear_ids()
		return True
	
	def jumpMove(self, src_menu, n1, dest_menu, n2): # new feature
		''' moves item or menu from source menu n1
		    to before destination menu n2
		    where n1 and n2 are integers representing tags in the menu
		    by a 0-based count before moving the item or menu,
		    (appends when n2 > 0-based count of tags in destination)
		    True when successful '''
		dom_mnu1 = self._get_dom_menu(src_menu)
		if dom_mnu1 is None:
			return False
		dom_mnu2 = self._get_dom_menu(dest_menu)
		if dom_mnu2 is None:
			return False
		i1 = self._get_real_num(src_menu, n1)
		if i1 is None:
			return False
		tmp = dom_mnu1.childNodes[i1].cloneNode(deep=True)
		dum = dom_mnu1.removeChild(dom_mnu1.childNodes[i1])
		dum.unlink() # should be unlinked if not used according to docs
		if src_menu == dest_menu and n1 < n2:
		    n2 -= 1
		i2 = self._get_real_num(dest_menu, n2)
		if i2 is None:
			dom_mnu2.insertBefore(tmp, None)
		else:
			dom_mnu2.insertBefore(tmp, dom_mnu2.childNodes[i2])
		self._clear_ids()
		return True

	def setItemProps(self, menu, n, label, action, exe):
		''' at position n (0-based DOM count) of menu (by ID)
		    sets the string label attribute and string action name, and
		    when action name is "Execute",
		        sets the item to have at least one command or execute tag
		        containing string exe (preferring command, as execute tag is
		        deprecated, and preferring the first matching tag found)
		    when action is anything else,
		        removes all other contents from the item '''
		itm = self._get_dom_item(menu,n)
		self._set_item_node_props(itm, label, action, exe)

	def setMenuLabel(self, menu, label):
		''' sets the label attribute of menu (by ID) to string label '''
		mnu = self._get_dom_menu(menu)
		if mnu:
			mnu.setAttribute("label", label)
			self._clear_ids()
	
	def getMenuLabel(self,menu):
		''' returns the string label attribute of menu (by ID)
		    or None if top level '''
		mnu = self._get_dom_menu(menu)
		if mnu:
			if mnu.hasAttribute("label"):
				return mnu.getAttribute("label")

	def setRefLabel(self, parent, mid, label):
		''' sets the string label of
		    the menu mid (by ID within the parent menu tree)
		    (Warning: not safe, because several links may have the same id) '''
		prnt = self._get_dom_menu(parent)
		if prnt: mnu = self._get_dom_ref(mid, prnt)
		if mnu:
			mnu.setAttribute("label", label)
			self._clear_ids()

	def setRefId(self, parent, mid, new_id):
		''' sets the id attribute of
		    the menu mid (by ID within the parent menu tree)
		    (Warning: not safe, because several links may have the same id) '''
		prnt = self._get_dom_menu(parent)
		if prnt: mnu = self._get_dom_ref(mid, prnt)
		if mnu:
			mnu.setAttribute("id", new_id)
			self._clear_ids()

	def setMenuExecute(self, parent, mid, execute):
		''' sets the execute attribute (the attribute NOT the execute tag)
		    of the menu mid (by ID within the parent menu tree)
		    (only use for pipe-menu, not for link or other menu) '''
		prnt = self._get_dom_menu(parent)
		if prnt: mnu = self._get_dom_ref(mid, prnt)
		if mnu: mnu.setAttribute("execute", execute)
			
	def getItem(self,menu,num): # unused
		''' Return properties dict for item/menu/sep at menu and view num '''
		mnu = self._get_dom_menu(menu)
		if not mnu: return
		n = 0
		for i in mnu.childNodes:
			if i.nodeType == i.ELEMENT_NODE:
				if n == num:
					if i.nodeName == "menu":
						return self._get_menu_props(i)
					elif i.nodeName == "separator":
						return self._get_sep_props(i)
					elif i.nodeName == "item":
						return self._get_item_props(i) #BUGFIX was missing _
				if i.nodeName in ("menu","separator","item"):
					n += 1
	
	def isMenu(self,menu):
		''' Returns True if it's an existing ID other than a link '''
		dom = self._get_dom_menu(menu, self._menu_is_non_link)
		if dom:
			return True
		else:
			return False
	
	def getMenu(self,menu):
		''' Returns a menu, as a list of dictionaries, not recursively.
		    Each dictionary has the item's properties. Empty if invalid menu '''
		mnu = self._get_dom_menu(menu)
		return self._get_menu_by_node(menu, mnu)

	def getMenuRecursive(self, menuid):
		''' Returns a whole menu, as a list of dictionaries.
		    Each dictionary has the item's properties.
		    Recursively includes lists of dictionaries for the contents of
		    menus, with "." as the key for the contents, because "." can't be
		    an XML tag or attribute and is a symbol for a directory itself. '''
		menu_content = self.menu.getMenu(menuid)
		for it in menu_content:
			if (it["type"] == "menu" and it["action"] != "Pipemenu"
			    and it["action"] != "Link"):
				it["."] = self.getMenuRecursive(it["id"])
		return menu_content

	def replaceId(self, old_id, new_id, parent=None):
		''' replaces all id's in menu matching old_id with new_id
		    parent should be omitted (when not None, it has dom node type) '''
		if not parent: parent = self.dom.documentElement
		for item in parent.childNodes:
			if item.nodeName == "menu":
				if (item.hasAttribute("id") and
				    item.getAttribute("id") == old_id or
				    not item.hasAttribute("id") and old_id is None):
					item.setAttribute("id", new_id)
				elif item.hasChildNodes():
					self.replaceId(old_id, new_id, item)
		self._clear_ids()

