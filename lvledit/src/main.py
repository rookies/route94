#!/usr/bin/python3
# -*- coding: utf-8 -*-
#  main.py
#  
#  Copyright 2013 Robert Knauer <robert@privatdemail.net>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import level3 as level
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject # python-gobject
from gi.repository.Gtk import Builder
import os.path
import math
import glob
import subprocess
import operator
import traceback
import re
import tempfile

class LevelEditor (object):
	IMGPATH = "../data/img/"
	SOUNDPATH = "../data/sound/"
	NUMBLOCKSY = 20.	
	builder = None
	metadata_store = None
	blockdefs_store = None
	blockdefs_store2 = None
	standard_blocks_store = None
	own_blocks_store = None
	items_store = None
	bgimg_store = None
	bgmusic_store = None
	zipfile_store = None
	level = level.Level()
	changed = False
	opened_file = None
	opened_filepath = ""
	level_pixmap = None
	block_images = []
	item_images = []
	messagedialog1_parent_dialog = None
	trashcoords = (0, 0)
	dragtype = 0
	notebook3_page = 0
	own_blocks_tmpfiles = {}
	tab2_blockdefs_rows = 0
	tab2_blocks_rows = 0
	
	def __init__(self):
		### READ FROM GUI FILE ###
		self.builder = Builder()
		self.builder.add_from_file("gui.glade")
		self.builder.connect_signals(self)
		### CREATE STUFF FOR THE METADATA TREEVIEW ###
		key = Gtk.TreeViewColumn("Schlüssel", Gtk.CellRendererText(), text=0)
		value = Gtk.TreeViewColumn("Wert", Gtk.CellRendererText(), text=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview1").append_column(key)
		self.builder.get_object("treeview1").append_column(value)
		## Create the model:
		self.metadata_store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
		## Assign the model to the TreeView:
		self.builder.get_object("treeview1").set_model(self.metadata_store)
		## Fill the model:
		self.update_metadata_store()
		### CREATE STUFF FOR THE BLOCKDEFS TREEVIEW #1 ###
		ident = Gtk.TreeViewColumn("ID", Gtk.CellRendererText(), text=0)
		deftype = Gtk.TreeViewColumn("Typ", Gtk.CellRendererText(), text=1)
		arg = Gtk.TreeViewColumn("Argument", Gtk.CellRendererText(), text=2)
		img = Gtk.TreeViewColumn("Vorschau", Gtk.CellRendererPixbuf(), pixbuf=3)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview2").append_column(ident)
		self.builder.get_object("treeview2").append_column(deftype)
		self.builder.get_object("treeview2").append_column(arg)
		self.builder.get_object("treeview2").append_column(img)
		## Create the model:
		self.blockdefs_store = Gtk.ListStore(GObject.TYPE_UINT, GObject.TYPE_STRING, GObject.TYPE_STRING, GdkPixbuf.Pixbuf)
		## Assign the model to the TreeView:
		self.builder.get_object("treeview2").set_model(self.blockdefs_store)
		## Fill the model:
		self.update_blockdefs_store()
		### CREATE STUFF FOR THE BLOCKDEFS TREEVIEW #2 ###
		ident = Gtk.TreeViewColumn("ID", Gtk.CellRendererText(), text=0)
		img = Gtk.TreeViewColumn("Vorschau", Gtk.CellRendererPixbuf(), pixbuf=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview3").append_column(ident)
		self.builder.get_object("treeview3").append_column(img)
		## Create the model:
		self.blockdefs_store2 = Gtk.ListStore(GObject.TYPE_UINT, GdkPixbuf.Pixbuf)
		## Assign the model to the TreeView:
		self.builder.get_object("treeview3").set_model(self.blockdefs_store2)
		## Fill the model:
		self.update_blockdefs_store2()
		### CREATE STUFF FOR THE STANDARD BLOCKS TREEVIEW ###
		name = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
		img = Gtk.TreeViewColumn("Vorschau", Gtk.CellRendererPixbuf(), pixbuf=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview4").append_column(name)
		self.builder.get_object("treeview4").append_column(img)
		## Create the model:
		self.standard_blocks_store = Gtk.ListStore(GObject.TYPE_STRING, GdkPixbuf.Pixbuf)
		## Assign the model to the TreeView:
		self.builder.get_object("treeview4").set_model(self.standard_blocks_store)
		## Fill the model:
		self.update_standard_blocks_store()
		### CREATE STUFF FOR THE OWN BLOCKS TREEVIEW ###
		name = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
		img = Gtk.TreeViewColumn("Vorschau", Gtk.CellRendererPixbuf(), pixbuf=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview9").append_column(name)
		self.builder.get_object("treeview9").append_column(img)
		## Create the model:
		self.own_blocks_store = Gtk.ListStore(GObject.TYPE_STRING, GdkPixbuf.Pixbuf)
		## Assign the model to the TreeView:
		self.builder.get_object("treeview9").set_model(self.own_blocks_store)
		## Fill the model:
		self.update_own_blocks_store()
		### CREATE STUFF FOR THE ITEMS TREEVIEW ###
		ident = Gtk.TreeViewColumn("ID", Gtk.CellRendererText(), text=0)
		img = Gtk.TreeViewColumn("Vorschau", Gtk.CellRendererPixbuf(), pixbuf=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview5").append_column(ident)
		self.builder.get_object("treeview5").append_column(img)
		## Create the model:
		self.items_store = Gtk.ListStore(GObject.TYPE_UINT, GdkPixbuf.Pixbuf)
		## Assign the model to the TreeView:
		self.builder.get_object("treeview5").set_model(self.items_store)
		## Fill the model:
		self.update_items_store()
		### CREATE STUFF FOR THE BGIMG TREEVIEW ###
		sel = Gtk.TreeViewColumn("Gewählt?", Gtk.CellRendererText(), text=0)
		name = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1)
		img = Gtk.TreeViewColumn("Vorschau", Gtk.CellRendererPixbuf(), pixbuf=2)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview6").append_column(sel)
		self.builder.get_object("treeview6").append_column(name)
		self.builder.get_object("treeview6").append_column(img)
		## Create the model:
		self.bgimg_store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GdkPixbuf.Pixbuf)
		## Assign the model to the treeview:
		self.builder.get_object("treeview6").set_model(self.bgimg_store)
		## Fill the model:
		self.update_bgimg_store()
		### CREATE STUFF FOR THE BGMUSIC TREEVIEW ###
		sel = Gtk.TreeViewColumn("Gewählt?", Gtk.CellRendererText(), text=0)
		name = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview7").append_column(sel)
		self.builder.get_object("treeview7").append_column(name)
		## Create the model:
		self.bgmusic_store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
		## Assign the model to the treeview:
		self.builder.get_object("treeview7").set_model(self.bgmusic_store)
		## Fill the model:
		self.update_bgmusic_store()
		### CREATE STUFF FOR THE ZIPFILE TREEVIEW ###
		size = Gtk.TreeViewColumn("Dateigröße", Gtk.CellRendererText(), text=0)
		name = Gtk.TreeViewColumn("Dateiname", Gtk.CellRendererText(), text=1)
		## Add the columns to the TreeView:
		self.builder.get_object("treeview8").append_column(size)
		self.builder.get_object("treeview8").append_column(name)
		## Create the model:
		self.zipfile_store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
		## Assign the model to the treeview:
		self.builder.get_object("treeview8").set_model(self.zipfile_store)
		## Fill the model:
		self.update_zipfile_store()
		### RESIZE LEVEL LAYOUT ###
		self.resize_level_layout()
		### ENABLE DRAG & DROP FOR THE LEVEL EDITOR ###
		self.builder.get_object("treeview3").drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
		self.builder.get_object("treeview3").drag_source_add_text_targets()
		self.builder.get_object("treeview5").drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
		self.builder.get_object("treeview5").drag_source_add_text_targets()
		self.builder.get_object("layout1").drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
		self.builder.get_object("layout1").drag_dest_add_text_targets()
		self.builder.get_object("layout1").drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE)
		self.builder.get_object("layout1").drag_source_add_text_targets()
		self.builder.get_object("image1").drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.MOVE)
		self.builder.get_object("image1").drag_dest_add_text_targets()
		### SET THE WINDOW TITLE ###
		self.update_window_title()
	def run(self):
		try:
			Gtk.main()
		except KeyboardInterrupt:
			self.quit()
	def quit(self):
		Gtk.main_quit()
		## Remove old temporary files:
		for name, tmpf in self.own_blocks_tmpfiles.items():
			os.unlink(tmpf)
		self.own_blocks_tmpfiles = {}
	def translate_coords(self, x, y):
		x_trans = math.floor(x/self.get_block_height())
		y_trans = math.floor((self.get_level_layout_height()-y)*2/self.get_block_height())
		return (x_trans, y_trans)
	def open_messagedialog1(self, text1, text2, parent_dlg):
		self.builder.get_object("messagedialog1").set_markup(text1)
		self.builder.get_object("messagedialog1").format_secondary_text(text2)
		self.builder.get_object("messagedialog1").set_visible(True)
		if parent_dlg is None:
			self.messagedialog1_parent_dialog = None
			self.builder.get_object("window1").set_sensitive(False)
		else:
			self.messagedialog1_parent_dialog = parent_dlg
			parent_dlg.set_sensitive(False)
	def update_everything(self, blockdefs=True, bgimgs=True, bgmusic=True, stdblocks=True):
		## Metadata Store:
		self.update_metadata_store()
		## Blockdefs Stores:
		if blockdefs:
			self.update_blockdefs_store()
			self.update_blockdefs_store2()
		## Standard blocks Store:
		if stdblocks:
			self.update_standard_blocks_store()
		## Own blocks Store:
		self.update_own_blocks_store()
		## Level layout:
		self.fill_block_images()
		## Window Title:
		self.update_window_title()
		## Level Width Scale:
		self.builder.get_object("adjustment1").set_value(self.level.get_level_width())
		self.update_levelwidth_scale_lower()
		## BG imgs:
		if bgimgs:
			self.update_bgimg_store()
		## BG music:
		if bgmusic:
			self.update_bgmusic_store()
		## Zip file:
		self.update_zipfile_store()
	def update_levelwidth_scale_lower(self):
		## get biggest block position:
		cols = self.level.get_columns()
		biggest = 0
		if len(cols) is not 0:
			for col in cols:
				if len(col["blocks"]) is not 0 and col["position"] > biggest:
					biggest = col["position"]
		## set lower:
		self.builder.get_object("adjustment1").set_lower(biggest+2)
	def update_standard_blocks_store(self):
		self.standard_blocks_store.clear()
		blocks = []
		for f in glob.glob(self.IMGPATH + "blocks/*.png"):
			name = os.path.basename(f).split(".", 2)[0]
			blocks.append((name, f))
		blocks.sort(key=operator.itemgetter(0))
		for name, f in blocks:
			img = Gtk.Image()
			img.set_from_file(f)
			self.standard_blocks_store.append([
				name,
				img.get_pixbuf().scale_simple(128, 64, GdkPixbuf.InterpType.NEAREST)
			])
	def update_own_blocks_store(self):
		## Remove old temporary files:
		for name, tmpf in self.own_blocks_tmpfiles.items():
			os.unlink(tmpf)
		self.own_blocks_tmpfiles = {}
		## Clear store:
		self.own_blocks_store.clear()
		blocks = []
		pattern = re.compile("^textures/.*\.png$")
		for f in self.level.zip_list():
			if pattern.match(f) is not None:
				name = os.path.basename(f).split(".", 2)[0]
				blocks.append((name, f))
		blocks.sort(key=operator.itemgetter(0))
		for name, f in blocks:
			tmpf = tempfile.mkstemp()
			self.level.zip_writeto(f, tmpf[1])
			img = Gtk.Image()
			img.set_from_file(tmpf[1])
			self.own_blocks_store.append([
				name,
				img.get_pixbuf().scale_simple(128, 64, GdkPixbuf.InterpType.NEAREST)
			])
			self.own_blocks_tmpfiles[name] = tmpf[1]
	def update_metadata_store(self):
		self.metadata_store.clear()
		for key, value in self.level.get_all_metadata().items():
			self.metadata_store.append([key, value])
	def update_blockdefs_store(self):
		self.blockdefs_store.clear()
		for bdef in self.level.get_blockdefs():
			img = self.get_image_from_blockdef_id(bdef["id"])
			if bdef["type"] == 1:
				t = "Standard"
			elif bdef["type"] == 2:
				t = "Spezial"
			elif bdef["type"] == 3:
				t = "level-spezifisch"
			else:
				t = "unbekannt"
			self.blockdefs_store.append([
				bdef["id"],
				t,
				str(bdef["arg"]),
				img.get_pixbuf().scale_simple(64, 32, GdkPixbuf.InterpType.NEAREST)
			])
			img.clear()
	def update_blockdefs_store2(self):
		self.blockdefs_store2.clear()
		for bdef in self.level.get_blockdefs():
			img = self.get_image_from_blockdef_id(bdef["id"])
			self.blockdefs_store2.append([
				bdef["id"],
				img.get_pixbuf().scale_simple(128, 64, GdkPixbuf.InterpType.NEAREST)
			])
			img.clear()
	def update_items_store(self):
		self.items_store.clear()
		i = 0
		for item in self.level.get_itemdefs():
			img = self.get_image_from_item_name(item)
			self.items_store.append([
				i,
				img.get_pixbuf()
			])
			i += 1
	def update_bgimg_store(self):
		self.bgimg_store.clear()
		bgimgs = []
		for f in glob.glob(self.IMGPATH + "backgrounds/*.png"):
			name = os.path.basename(f).split(".", 2)[0]
			bgimgs.append((name, f))
		bgimgs.sort(key=operator.itemgetter(0))
		x = self.level.get_bgimg()
		## Append custom bgimg:
		if x[0] and x[1] == "":
			t = "X"
		else:
			t = ""
		self.bgimg_store.append([
			t,
			"<Eigenes Hintergrundbild vom ZIP-Archiv>",
			None
		])
		## Append standard bgimgs:
		for name, f in bgimgs:
			img = Gtk.Image()
			img.set_from_file(f)
			pb = img.get_pixbuf()
			if x[0] and x[1] == name:
				t = "X"
			else:
				t = ""
			self.bgimg_store.append([
				t,
				name,
				pb.scale_simple(pb.get_width()/4., pb.get_height()/4., GdkPixbuf.InterpType.NEAREST)
			])
	def update_bgmusic_store(self):
		self.bgmusic_store.clear()
		bgm = []
		for f in glob.glob(self.SOUNDPATH + "backgrounds/*.ogg"):
			name = os.path.basename(f).split(".", 2)[0]
			bgm.append(name)
		bgm.sort()
		x = self.level.get_bgmusic()
		## Append custom bgmusic:
		if x[0] and x[1] == "":
			t = "X"
		else:
			t = ""
		self.bgmusic_store.append([
			t,
			"<Eigene Hintergrundmusik vom ZIP-Archiv>"
		])
		## Append standard bgmusics:
		for name in bgm:
			if x[0] and x[1] == name:
				t = "X"
			else:
				t = ""
			self.bgmusic_store.append([ t, name ])
	def update_zipfile_store(self):
		self.zipfile_store.clear()
		for f in self.level.zip_info():
			self.zipfile_store.append([
				"%d" % f.file_size,
				f.filename
			])
	def update_window_title(self):
		## Check for unsaved file:
		if self.changed:
			t = "*"
		else:
			t = ""
		## Check for the filename:
		if self.opened_file is None:
			t += "unnamed"
		else:
			t += str(self.opened_file)
		## Append the program name & version:
		t += " - CAPSAICIN LevelEditor v0.1"
		## Set title:
		self.builder.get_object("window1").set_title(t)
	def ask_for_discarding_changes(self):
		dlg = Gtk.MessageDialog(parent=self.builder.get_object("window1"))
		dlg.add_buttons(Gtk.STOCK_CANCEL, 1, Gtk.STOCK_OK, 2)
		dlg.set_markup("Ungespeicherte Änderungen")
		dlg.format_secondary_text("Die aktuelle Datei wurde seit der letzten Änderung nicht gespeichert. Änderungen verwerfen?")
		res = dlg.run()
		dlg.destroy()
		if res == 1:
			return False
		else:
			return True
	def get_image_from_blockdef_id(self, ident):
		img = Gtk.Image()
		bdef = self.level.get_blockdef_by_id(ident)
		if bdef is None or bdef[0] not in [1, 3]:
			fname = self.IMGPATH + "block_not_found.png"
		elif bdef[0] == 1:
			if os.path.exists(self.IMGPATH + "blocks/" + bdef[1] + ".png"):
				fname = self.IMGPATH + "blocks/" + bdef[1] + ".png"
			else:
				fname = self.IMGPATH + "block_not_found.png"
		elif bdef[0] == 3:
			if bdef[1] in self.own_blocks_tmpfiles and os.path.exists(self.own_blocks_tmpfiles[bdef[1]]):
				fname = self.own_blocks_tmpfiles[bdef[1]]
			else:
				fname = self.IMGPATH + "block_not_found.png"
		img.set_from_file(fname)
		return img
	def get_image_from_item_id(self, ident):
		defs = self.level.get_itemdefs()
		if len(defs) <= ident:
			img = Gtk.Image()
			img.set_from_file(self.IMGPATH + "item_not_found.png")
		else:
			name = defs[ident]
			img = self.get_image_from_item_name(name)
		return img
	def get_image_from_item_name(self, name):
		img = Gtk.Image()
		if os.path.exists(self.IMGPATH + "items/" + name + ".png"):
			fname = self.IMGPATH + "items/" + name + ".png"
		else:
			fname = self.IMGPATH + "item_not_found.png"
		img.set_from_file(fname)
		return img
	def get_level_layout_height(self):
		return self.builder.get_object("layout1").get_allocation().height
	def get_block_height(self):
		return self.get_level_layout_height()/20.
	def resize_level_layout(self):
		layout = self.builder.get_object("layout1")
		layout.set_size((self.level.get_level_width()+1)*self.get_block_height(), layout.get_size()[1])
	def fill_block_images(self):
		# Calculate sizes:
		layout = self.builder.get_object("layout1")
		height = layout.get_allocation().height
		block_height = height/self.NUMBLOCKSY
		self.resize_level_layout()
		# Clear block images:
		for img in self.block_images:
			img.clear()
		del self.block_images[:]
		# Clear item images:
		for img in self.item_images:
			img.clear()
		del self.item_images[:]
		# Run through columns:
		i = 0
		j = 0
		for col in self.level.get_columns():
			# Add blocks:
			for blk in col["blocks"]:
				self.block_images.append(self.get_image_from_blockdef_id(blk["blockdef"]))
				self.block_images[i].set_from_pixbuf(self.block_images[i].get_pixbuf().scale_simple(block_height*2, block_height, GdkPixbuf.InterpType.NEAREST))
				layout.put(self.block_images[i], col["position"]*block_height, height-(((blk["position"]/2.)+0.5)*block_height))
				i += 1
			# Add items:
			for itm in col["items"]:
				self.item_images.append(self.get_image_from_item_id(itm["id"]))
				self.item_images[j].set_from_pixbuf(self.item_images[j].get_pixbuf().scale_simple(block_height*.8, block_height*.8, GdkPixbuf.InterpType.NEAREST))
				layout.put(self.item_images[j], (col["position"]+.1)*block_height, height-(((itm["position"]/2.)+0.5)*block_height))
				j += 1
		self.builder.get_object("layout1").show_all()
	def add_block(self, x, y, bdef):
		x_trans, y_trans = self.translate_coords(x,y)
		print("Blockdef #%d received on x=%d; y=%d; x_trans=%d; y_trans=%d" % (bdef, x, y, x_trans, y_trans))
		if x_trans >= self.level.get_level_width()-1 or y_trans > 30:
			self.open_messagedialog1("Fehler beim Platzieren des Blocks!", "Der Block kann nicht außerhalb des Level-Bereichs abgelegt werden!", None)
		else:
			self.level.add_block(x_trans, y_trans, bdef)
			self.changed = True
			self.update_everything(False, False)
	def rm_block_raw(self, x, y):
		x_trans, y_trans = self.translate_coords(x,y)
		self.rm_block(x_trans, y_trans)
	def rm_block(self, x, y):
		if y < 30:
			if self.level.remove_block(x, y):
				self.changed = True
				self.update_everything(False, False)
				print("Block deleted on x_trans=%d; y_trans=%d" % (x,y))
	def add_item(self, x, y, iid):
		x_trans, y_trans = self.translate_coords(x,y)
		print("Item #%d received on x=%d; y=%d; x_trans=%d; y_trans=%d" % (iid, x, y, x_trans, y_trans))
		if x_trans >= self.level.get_level_width()-1 or y_trans > 30:
			self.open_messagedialog1("Fehler beim Platzieren des Items!", "Das Item kann nicht außerhalb des Level-Bereichs abgelegt werden!", None)
		else:
			self.level.add_item(x_trans, y_trans, iid)
			self.changed = True
			self.update_everything(False, False)
	def rm_item_raw(self, x, y):
		x_trans, y_trans = self.translate_coords(x,y)
		self.rm_item(x_trans, y_trans)
	def rm_item(self, x, y):
		if y < 30:
			if self.level.remove_item(x, y):
				self.changed = True
				self.update_everything(False, False)
				print("Item deleted on x_trans=%d; y_trans=%d" % (x,y))
	### window1 EVENTS ###
	def on_window1_delete_event(self, *args):
		# closed
		if not self.changed or self.ask_for_discarding_changes():
			self.quit()
			return False
		return True
	def on_imagemenuitem1_activate(self, *args):
		# file -> new
		if not self.changed or self.ask_for_discarding_changes():
			self.level.cleanup()
			self.changed = False
			self.opened_file = None
			self.opened_filepath = ""
			self.update_everything()
	def on_imagemenuitem2_activate(self, *args):
		# file -> open
		self.builder.get_object("filechooserdialog2").set_visible(True)
	def on_imagemenuitem3_activate(self, *args):
		# file -> save
		if self.opened_file is None:
			self.builder.get_object("filechooserdialog1").set_visible(True)
		else:
			try:
				self.level.write(self.opened_filepath)
			except BaseException as e:
				self.open_messagedialog1("Fehler beim Speichern!", str(e), None)
			else:
				self.changed = False
				self.update_everything()
	def on_imagemenuitem4_activate(self, *args):
		# file -> save as
		self.builder.get_object("filechooserdialog1").set_visible(True)
	def on_imagemenuitem5_activate(self, *args):
		# file -> quit
		if not self.changed or self.ask_for_discarding_changes():
			self.quit()
	def on_imagemenuitem10_activate(self, *args):
		# help -> about
		self.builder.get_object("aboutdialog1").set_visible(True)
	def on_imagemenuitem11_activate(self, *args):
		# view -> open in game
		if self.opened_file is None or self.changed:
			self.open_messagedialog1("Level nicht gespeichert!", "Um das Level im Spiel zu öffnen muss es vorher gespeichert werden!", None)
		else:
			### TODO: open game with c18h27no3 load <file>
			subprocess.call([
				"../c18h27no3",
				"load",
				self.opened_filepath
			])
	def on_window1_size_allocate(self, *args):
		# size changed
		self.builder.get_object("scrolledwindow1").set_size_request(args[1].width*0.75, -1)
		self.resize_level_layout()
	### aboutdialog1 EVENTS ###
	def on_aboutdialog1_delete_event(self, *args):
		# closed
		self.builder.get_object("aboutdialog1").set_visible(False)
		return True
	def on_aboutdialog_action_area1_button_press_event(self, *args):
		# close pressed
		self.builder.get_object("aboutdialog1").set_visible(False)
	### window1/tab1 EVENTS ###
	def on_button1_clicked(self, *args):
		# new pressed
		self.builder.get_object("dialog2").set_visible(True)
		self.builder.get_object("window1").set_sensitive(False)
	def on_button2_clicked(self, *args):
		# edit pressed
		row = self.builder.get_object("treeview-selection1").get_selected_rows()
		self.builder.get_object("entry4").set_text(row[0].get_value(row[0].get_iter(row[1][0]), 0))
		self.builder.get_object("entry5").set_text(row[0].get_value(row[0].get_iter(row[1][0]), 1))
		self.builder.get_object("dialog3").set_visible(True)
		self.builder.get_object("window1").set_sensitive(False)
	def on_button3_clicked(self, *args):
		# delete pressed
		self.builder.get_object("dialog1").set_visible(True)
		self.builder.get_object("window1").set_sensitive(False)
	def on_treeview_selection1_changed(self, *args):
		# treeview selection changed
		selected = self.builder.get_object("treeview-selection1").count_selected_rows()
		if selected == 1:
			# Allow editing:
			self.builder.get_object("button2").set_sensitive(True)
			# Allow deleting:
			self.builder.get_object("button3").set_sensitive(True)
		elif selected > 1:
			# Disable editing:
			self.builder.get_object("button2").set_sensitive(False)
			# Allow deleting:
			self.builder.get_object("button3").set_sensitive(True)
		else:
			# Disable editing:
			self.builder.get_object("button2").set_sensitive(False)
			# Disable deleting:
			self.builder.get_object("button3").set_sensitive(False)
	### window1/tab2 EVENTS ###
	def update_tab2_buttons(self):
		if self.tab2_blockdefs_rows == 1:
			# allow deleting
			self.builder.get_object("button17").set_sensitive(True)
			if self.tab2_blocks_rows == 1:
				# allow editing
				self.builder.get_object("button16").set_sensitive(True)
			else:
				# deny editing
				self.builder.get_object("button16").set_sensitive(False)
		else:
			# deny deleting
			self.builder.get_object("button17").set_sensitive(False)
			# deny editing
			self.builder.get_object("button16").set_sensitive(False)
		
		if self.tab2_blocks_rows == 1:
			# allow adding
			self.builder.get_object("button15").set_sensitive(True)
			if self.tab2_blockdefs_rows == 1:
				# allow editing
				self.builder.get_object("button16").set_sensitive(True)
			else:
				# deny editing
				self.builder.get_object("button16").set_sensitive(False)
		else:
			# deny adding
			self.builder.get_object("button15").set_sensitive(False)
			# deny editing
			self.builder.get_object("button16").set_sensitive(False)
	def on_treeview_selection2_changed(self, widget):
		## blockdefs
		self.tab2_blockdefs_rows = widget.count_selected_rows()
		self.update_tab2_buttons()
	def on_treeview_selection4_changed(self, widget):
		## standard blocks
		self.tab2_blocks_rows = widget.count_selected_rows()
		self.update_tab2_buttons()
	def on_treeview_selection9_changed(self, widget):
		## custom blocks
		self.tab2_blocks_rows = widget.count_selected_rows()
		self.update_tab2_buttons()
	def on_notebook2_switch_page(self, widget, frame, page):
		if page == 0:
			self.tab2_blocks_rows = self.builder.get_object("treeview-selection4").count_selected_rows()
		elif page == 1:
			self.tab2_blocks_rows = 0
		elif page == 2:
			self.tab2_blocks_rows = self.builder.get_object("treeview-selection9").count_selected_rows()
		self.update_tab2_buttons()
	def on_button18_clicked(self, widget, *args):
		## reload
		self.update_everything()
	def on_button15_clicked(self, widget, *args):
		## add
		if self.builder.get_object("notebook2").get_current_page() == 0:
			row = self.builder.get_object("treeview-selection4").get_selected()
			t = 1
		elif self.builder.get_object("notebook2").get_current_page() == 2:
			row = self.builder.get_object("treeview-selection9").get_selected()
			t = 3
		block = row[0].get_value(row[1], 0)
		self.level.add_blockdef(t, block)
		self.changed = True
		self.update_everything(True, False, False, False)
	def on_button16_clicked(self, widget, *args):
		## edit
		if self.builder.get_object("notebook2").get_current_page() == 0:
			row_block = self.builder.get_object("treeview-selection4").get_selected()
			t = 1
		elif self.builder.get_object("notebook2").get_current_page() == 2:
			row_block = self.builder.get_object("treeview-selection9").get_selected()
			t = 3
		row_bdef = self.builder.get_object("treeview-selection2").get_selected()
		block = row_block[0].get_value(row_block[1], 0)
		bdef = int(row_bdef[0].get_value(row_bdef[1], 0))
		self.level.update_blockdef(bdef, t, block)
		self.changed = True
		self.update_everything(True, False, False, False)
	def on_button17_clicked(self, widget, *args):
		## delete
		row = self.builder.get_object("treeview-selection2").get_selected()
		bdef = int(row[0].get_value(row[1], 0))
		# check if the blockdef is used:
		used = False
		for col in self.level.get_columns():
			for blk in col["blocks"]:
				if blk["blockdef"] == bdef:
					used = True
					break
			if used is True:
				break
		if used:
			self.open_messagedialog1("Fehler beim Löschen!", "Die Blockdefinition kann nicht gelöscht werden, da sie noch von Blöcken verwendet wird!", None)
		else:
			self.level.del_blockdef(bdef)
			self.changed = True
			self.update_everything(True, False, False, False)
	
	### window1/tab3 EVENTS ###
	def on_button19_clicked(self, widget, *args):
		# Set bgimg
		tv = self.builder.get_object("treeview6")
		row = tv.get_selection().get_selected()
		if row[1] is None:
			self.level.unset_bgimg()
		else:
			if row[0].get_path(row[1]).get_indices()[0] == 0:
				self.level.set_bgimg("")
			else:
				self.level.set_bgimg(row[0].get_value(row[1], 1))
		self.changed = True
		self.update_everything()
	def on_button20_clicked(self, widget, *args):
		# Unset bgimg
		self.level.unset_bgimg()
		self.changed = True
		self.update_everything()
	def on_button21_clicked(self, widget, *args):
		# Set bgmusic
		tv = self.builder.get_object("treeview7")
		row = tv.get_selection().get_selected()
		if row[1] is None:
			self.level.unset_bgmusic()
		else:
			if row[0].get_path(row[1]).get_indices()[0] == 0:
				self.level.set_bgmusic("")
			else:
				self.level.set_bgmusic(row[0].get_value(row[1], 1))
		self.changed = True
		self.update_everything()
	def on_button22_clicked(self, widget, *args):
		# Unset bgmusic
		self.level.unset_bgmusic()
		self.changed = True
		self.update_everything()
	
	### window1/tab4 EVENTS ###
	def on_notebook3_switch_page(self, widget, child, num):
		self.notebook3_page = num
	def on_scale1_format_value(self, widget, value):
		return "%d" % value
	def on_scale1_change_value(self, widget, scroll, value):
		lower = self.builder.get_object("adjustment1").get_lower()
		if int(value) < lower:
			value = lower
		self.level.set_level_width(value)
		if not self.changed:
			self.changed = True
			self.update_window_title()
		self.resize_level_layout()
	def on_treeview3_drag_begin(self, widget, dragctx):
		row = self.builder.get_object("treeview-selection3").get_selected()
		if row[1] is not None:
			img = self.get_image_from_blockdef_id(row[0].get_value(row[1], 0))
			widget.drag_source_set_icon_pixbuf(img.get_pixbuf().scale_simple(64, 32, GdkPixbuf.InterpType.NEAREST))
			img.clear()
			self.dragtype = 1
	def on_treeview3_drag_data_get(self, widget, dragctx, selection, info, time):
		row = self.builder.get_object("treeview-selection3").get_selected()
		if row[1] is not None:
			selection.set_text(str(row[0].get_value(row[1], 0)), 1)
	def on_treeview3_drag_end(self, widget, dragctx):
		widget.drag_source_set_icon_stock("")
	def on_treeview5_drag_begin(self, widget, dragctx):
		row = self.builder.get_object("treeview5").get_selection().get_selected()
		if row[1] is not None:
			img = self.get_image_from_item_id(row[0].get_value(row[1], 0))
			widget.drag_source_set_icon_pixbuf(img.get_pixbuf())
			img.clear()
			self.dragtype = 2
	def on_treeview5_drag_data_get(self, widget, dragctx, selection, info, time):
		row = self.builder.get_object("treeview5").get_selection().get_selected()
		if row[1] is not None:
			selection.set_text(str(row[0].get_value(row[1], 0)), 1)
	def on_treeview5_drag_end(self, widget, dragctx):
		widget.drag_source_set_icon_stock("")
	def on_layout1_drag_data_received(self, widget, dragctx, x, y, selection, info, time):
		x += self.builder.get_object("adjustment2").get_value()
		if self.dragtype is 1:
			bdef = int(selection.get_text())
			self.add_block(x,y,bdef)
		elif self.dragtype is 2:
			iid = int(selection.get_text())
			self.add_item(x,y,iid)
		else:
			print("Unknown dragtype!")
	def on_layout1_button_press_event(self, widget, ev):
		if ev.button is 1:
			# left click -> add
			if self.notebook3_page is 0:
				# block
				row = self.builder.get_object("treeview3").get_selection().get_selected()
				if row[1] is not None:
					self.add_block(ev.x, ev.y, row[0].get_value(row[1], 0))
			elif self.notebook3_page is 1:
				# item
				row = self.builder.get_object("treeview5").get_selection().get_selected()
				if row[1] is not None:
					self.add_item(ev.x, ev.y, row[0].get_value(row[1], 0))
		elif ev.button is 3:
			# right click -> remove
			if self.notebook3_page is 0:
				# block
				self.rm_block_raw(ev.x, ev.y)
			elif self.notebook3_page is 1:
				# item
				self.rm_item_raw(ev.x, ev.y)
	def on_layout1_draw(self, widget, ctx):
		s = widget.get_allocation()
		block_height = s.height/self.NUMBLOCKSY
		block_width = 2*block_height
		ctx.set_source_rgb(1,1,1)
		ctx.paint()
		# Horizontal lines:
		ctx.set_source_rgb(0,0,0)
		ctx.set_line_width(1)
		for i in range(15):
			ctx.move_to(0, s.height-((i+1)*block_height))
			ctx.line_to(s.width, s.height-((i+1)*block_height))
			ctx.stroke()
		ctx.set_source_rgb(0.5,0.5,0.5)
		ctx.set_line_width(0.5)
		for i in range(29):
			ctx.move_to(0, s.height-(((i/2.)+0.5)*block_height))
			ctx.line_to(s.width, s.height-(((i/2.)+0.5)*block_height))
			ctx.stroke()
		# Vertical lines:
		ctx.set_source_rgb(0,0,0)
		ctx.set_line_width(1)
		offset = self.builder.get_object("adjustment2").get_value()
		offset -= block_width*int(offset/block_width)
		for i in range(int(s.width/(block_width)+1)):
			ctx.move_to(((i+1)*block_width)-offset, 5*block_height)
			ctx.line_to(((i+1)*block_width)-offset, s.height)
			ctx.stroke()
		ctx.set_source_rgb(0.5,0.5,0.5)
		ctx.set_line_width(0.5)
		for i in range(int(s.width/(block_width/2.))+1):
			ctx.move_to((((i/2.)+0.5)*block_width)-offset, s.height)
			ctx.line_to((((i/2.)+0.5)*block_width)-offset, 5*block_height)
			ctx.stroke()
		ctx.paint_with_alpha(0)
	def on_layout1_drag_begin(self, widget, dragctx):
		m = widget.get_pointer()
		x_trans, y_trans = self.translate_coords(m[0],m[1])
		self.trashcoords = (x_trans, y_trans)
	def on_image1_drag_drop(self, *args):
		if self.notebook3_page is 0:
			self.rm_block(self.trashcoords[0], self.trashcoords[1])
		elif self.notebook3_page is 1:
			self.rm_item(self.trashcoords[0], self.trashcoords[1])
		self.trashcoords = (0,0)
	### window1/tab5 EVENTS ###
	def on_treeview_selection8_changed(self, widget, *args):
		if widget.count_selected_rows() == 1:
			# allow extracting
			self.builder.get_object("button24").set_sensitive(True)
			# allow deleting
			self.builder.get_object("button25").set_sensitive(True)
			# allow renaming
			self.builder.get_object("button26").set_sensitive(True)
		else:
			# deny extracting
			self.builder.get_object("button24").set_sensitive(False)
			# deny deleting
			self.builder.get_object("button25").set_sensitive(False)
			# deny renaming
			self.builder.get_object("button26").set_sensitive(False)
	def on_button23_clicked(self, widget, *args):
		# Add file
		dlg = Gtk.FileChooserDialog("Datei hinzufügen", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, 1, Gtk.STOCK_OK, 2))
		dlg.set_default_response(2)
		res = dlg.run()
		if res == 2:
			f = dlg.get_filename()
			dlg2 = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, "Dateiname eingeben")
			dlg2.set_default_response(2)
			entry = Gtk.Entry()
			entry.set_text(os.path.basename(f))
			dlg2.vbox.pack_end(entry, True, True, 0)
			dlg2.show_all()
			if dlg2.run() == -5:
				self.level.zip_add(f, entry.get_text())
				print("Added zip entry '%s' from '%s'." % (entry.get_text(), f))
				self.changed = True
				self.update_everything()
			dlg2.destroy()
		dlg.destroy()
	def on_button24_clicked(self, widget, *args):
		# Extract file
		row = self.builder.get_object("treeview8").get_selection().get_selected()
		if row[1] is not None:
			f = row[0].get_value(row[1], 1)
			dlg = Gtk.FileChooserDialog("Datei extrahieren", None, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, 1, Gtk.STOCK_OK, 2))
			dlg.set_default_response(2)
			res = dlg.run()
			if res == 2:
				self.level.zip_extract(f, dlg.get_filename())
				print("Exported zip entry '%s' to '%s'." % (f, dlg.get_filename()))
			dlg.destroy()
	def on_button25_clicked(self, widget, *args):
		# Delete file
		row = self.builder.get_object("treeview8").get_selection().get_selected()
		if row[1] is not None:
			f = row[0].get_value(row[1], 1)
			dlg = Gtk.MessageDialog(parent=self.builder.get_object("window1"))
			dlg.add_buttons(Gtk.STOCK_CANCEL, 1, Gtk.STOCK_OK, 2)
			dlg.set_markup("Datei löschen?")
			dlg.format_secondary_text("Soll die Datei '%s' wirklich gelöscht werden?" % f)
			res = dlg.run()
			dlg.destroy()
			if res == 2:
				self.level.zip_remove(f)
				self.changed = True
				self.update_everything()
				print("Deleted zip entry '%s'." % f)
	def on_button26_clicked(self, widget, *args):
		# Rename file
		row = self.builder.get_object("treeview8").get_selection().get_selected()
		if row[1] is not None:
			f = row[0].get_value(row[1], 1)
			dlg = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK, "Dateiname eingeben")
			dlg.set_default_response(2)
			entry = Gtk.Entry()
			entry.set_text(f)
			dlg.vbox.pack_end(entry, True, True, 0)
			dlg.show_all()
			if dlg.run() == -5:
				self.level.zip_rename(f, entry.get_text())
				print("Renamed zip entry from '%s' to '%s'." % (f, entry.get_text()))
				self.changed = True
				self.update_everything()
			dlg.destroy()
	### scrolledwindow1 EVENTS ###
	def on_adjustment2_value_changed(self, widget):
		#print(self.builder.get_object("adjustment2").get_value())
		#print(widget.get_upper())
		pass
	### dialog1 (delete metadata) EVENTS ###
	def on_dialog1_delete_event(self, *args):
		# closed
		self.builder.get_object("dialog1").set_visible(False)
		self.builder.get_object("window1").set_sensitive(True)
		return True
	def on_button4_clicked(self, *args):
		# no button pressed
		self.builder.get_object("dialog1").set_visible(False)
		self.builder.get_object("window1").set_sensitive(True)
	def on_button5_clicked(self, *args):
		# yes button pressed
		rows = self.builder.get_object("treeview-selection1").get_selected_rows()
		for item in rows[1]:
			self.level.delete_metadata(rows[0].get_value(rows[0].get_iter(item), 0))
		self.changed = True
		self.update_everything()
		self.builder.get_object("dialog1").set_visible(False)
		self.builder.get_object("window1").set_sensitive(True)
	### filechooserdialog1 (save) EVENTS ###
	def on_filechooserdialog1_delete_event(self, *args):
		# closed
		self.builder.get_object("filechooserdialog1").set_visible(False)
		return True
	def on_button6_clicked(self, *args):
		# abort pressed
		self.builder.get_object("filechooserdialog1").set_visible(False)
	def on_button7_clicked(self, *args):
		# save pressed
		fname = self.builder.get_object("filechooserdialog1").get_filename()
		if fname is None:
			self.open_messagedialog1("Keine Datei ausgewählt!", "Zum Speichern muss eine Datei ausgewählt werden!", None)
		else:
			if os.path.exists(fname):
				dlg = Gtk.MessageDialog(parent=self.builder.get_object("window1"))
				dlg.add_buttons(Gtk.STOCK_CANCEL, 1, Gtk.STOCK_OK, 2)
				dlg.set_markup("Datei existiert bereits")
				dlg.format_secondary_text("Der ausgewählte Dateiname existiert bereits! Trotzdem speichern?")
				res = dlg.run()
				dlg.destroy()
				if res == 1:
					okay = False
				else:
					okay = True
			else:
				okay = True
			if okay:
				try:
					self.level.write(fname)
				except BaseException as e:
					self.open_messagedialog1("Fehler beim Speichern!", str(e), None)
					traceback.print_exc()
				else:
					self.changed = False
					self.opened_file = os.path.basename(fname)
					self.opened_filepath = fname
					self.update_everything(False, False)
				self.builder.get_object("filechooserdialog1").set_visible(False)
	### filechooserdialog2 (open) EVENTS ###
	def on_filechooserdialog2_delete_event(self, *args):
		# closed
		self.builder.get_object("filechooserdialog2").set_visible(False)
		return True
	def on_button8_clicked(self, *args):
		# abort pressed
		self.builder.get_object("filechooserdialog2").set_visible(False)
	def on_button9_clicked(self, *args):
		# open pressed
		if self.changed:
			if not self.ask_for_discarding_changes():
				self.builder.get_object("filechooserdialog2").set_visible(False)
				return
		fname = self.builder.get_object("filechooserdialog2").get_filename()
		try:
			self.level.read(fname)
			self.level.dump()
		except Exception as e:
			self.open_messagedialog1("Ungültige Datei!", str(e), None)
		else:
			### IMPORTANT: update all stuff ###
			self.changed = False
			self.opened_file = os.path.basename(fname)
			self.opened_filepath = fname
			self.update_everything()
			self.builder.get_object("filechooserdialog2").set_visible(False)
	### dialog2 (add metadata) EVENTS ###
	def on_dialog2_delete_event(self, *args):
		# closed
		self.builder.get_object("dialog2").set_visible(False)
		self.builder.get_object("window1").set_sensitive(True)
		return True
	def on_button10_clicked(self, *args):
		# abort button pressed
		self.builder.get_object("dialog2").set_visible(False)
		self.builder.get_object("entry2").set_text("")
		self.builder.get_object("entry3").set_text("")
		self.builder.get_object("window1").set_sensitive(True)
	def on_button11_clicked(self, *args):
		# add button pressed
		key = self.builder.get_object("entry2").get_text().strip()
		value = self.builder.get_object("entry3").get_text().strip()
		if key in self.level.get_all_metadata():
			self.open_messagedialog1("Ungültiger Schlüssel!", "Dieser Schlüssel wird bereits verwendet!", self.builder.get_object("dialog2"))
		elif len(key) > 65535 or len(key) == 0:
			self.open_messagedialog1("Ungültiger Schlüssel!", "Der Schlüssel entspricht nicht der zulässigen Zeichen-Anzahl! (1 bis 65535 Zeichen)", self.builder.get_object("dialog2"))
		elif len(value) > 16383 or len(value) == 0:
			self.open_messagedialog1("Ungültiger Wert!", "Der Wert entspricht nicht der zulässigen Zeichen-Anzahl! (1 bis 16383 Zeichen)", self.builder.get_object("dialog2"))
		else:
			self.level.set_metadata(key, value)
			self.changed = True
			self.update_everything()
			self.builder.get_object("dialog2").set_visible(False)
			self.builder.get_object("entry2").set_text("")
			self.builder.get_object("entry3").set_text("")
			self.builder.get_object("window1").set_sensitive(True)
	### dialog3 (edit metadata) EVENTS ###
	def on_dialog3_delete_event(self, *args):
		# closed
		self.builder.get_object("dialog3").set_visible(False)
		self.builder.get_object("window1").set_sensitive(True)
		return True
	def on_button12_clicked(self, *args):
		# abort button pressed
		self.builder.get_object("dialog3").set_visible(False)
		self.builder.get_object("window1").set_sensitive(True)
	def on_button13_clicked(self, *args):
		# submit button pressed
		key = self.builder.get_object("entry4").get_text()
		value = self.builder.get_object("entry5").get_text().strip()
		if len(value) > 16383 or len(value) == 0:
			self.open_messagedialog1("Ungültiger Wert!", "Der Wert entspricht nicht der zulässigen Zeichen-Anzahl! (1 bis 16383 Zeichen)", self.builder.get_object("dialog3"))
		else:
			self.level.set_metadata(key, value)
			self.changed = True
			self.update_everything()
			self.builder.get_object("dialog3").set_visible(False)
			self.builder.get_object("entry4").set_text("")
			self.builder.get_object("entry5").set_text("")
			self.builder.get_object("window1").set_sensitive(True)
	### messagedialog1 EVENTS ###
	def on_messagedialog1_delete_event(self, *args):
		# closed
		self.builder.get_object("messagedialog1").set_visible(False)
		if self.messagedialog1_parent_dialog is None:
			self.builder.get_object("window1").set_sensitive(True)
		else:
			self.messagedialog1_parent_dialog.set_sensitive(True)
		return True
	def on_button14_clicked(self, *args):
		# okay button pressed
		self.builder.get_object("messagedialog1").set_visible(False)
		if self.messagedialog1_parent_dialog is None:
			self.builder.get_object("window1").set_sensitive(True)
		else:
			self.messagedialog1_parent_dialog.set_sensitive(True)

if __name__ == "__main__":
	app = LevelEditor()
	app.run()
