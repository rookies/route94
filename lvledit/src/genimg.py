#!/usr/bin/python3
#  genimg.py
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
from PIL import Image, ImageDraw, ImageFont
import os
import os.path
import sys
import tempfile

class ImgGenerator (object):
	DATADIR = "../data/"
	IMGPATH = DATADIR+"img/"
	FONTPATH = DATADIR+"fonts/"
	NUMBLOCKSY = 20.
	level = None
	blk_sizes = (0,0)
	img_sizes = (0,0)
	image = None
	blkdef_images = {}
	item_images = []
	
	def __init__(self, path):
		print("==> Loading level...")
		self.level = level.Level()
		self.level.read(path)
		self.level.dump()
	def generate(self, height):
		# Calculate sizes:
		print("==> Starting generation...")
		self.blk_sizes = (
			int(height/10),
			int(height/20)
		)
		print("Block Size: %dx%d px" % self.blk_sizes)
		self.img_sizes = (
			int(self.blk_sizes[0]*self.level.get_level_width()/2),
			int(self.blk_sizes[1]*20)
		)
		print("Image Size: %dx%d px" % self.img_sizes)
		# Create image:
		self.image = Image.new("RGB", self.img_sizes, "white")
		# Create bgimg:
		x = self.level.get_bgimg()
		d = None
		if x[0]:
			if x[1] == "":
				d = tempfile.mkdtemp()
				self.level.zip_extract("background.png", d)
				img = os.path.join(d, "background.png")
			else:
				img = os.path.join(self.IMGPATH, "backgrounds", x[1]+".png")
			if os.path.exists(img):
				img = Image.open(img)
				img = img.convert("RGBA")
				img = img.resize((int(img.size[0]*(self.img_sizes[1]/img.size[1])),self.img_sizes[1]), Image.NEAREST)
				self.image.paste(img, (0,0), img)
			if d:
				os.unlink(os.path.join(d, "background.png"))
				os.rmdir(d)
		# Create block textures:
		tmpfiles = []
		for d in self.level.get_blockdefs():
			if d["type"] is 1:
				img = self.IMGPATH+"blocks/"+d["arg"]+".png"
				if not os.path.exists(img):
					img = self.IMGPATH+"block_not_found.png"
			elif d["type"] is 3:
				tmp = tempfile.mkstemp()[1]
				try:
					self.level.zip_writeto("textures/"+d["arg"]+".png", tmp)
					img = tmp
				except KeyError:
					img = self.IMGPATH+"block_not_found.png"
				tmpfiles.append(tmp)
			else:
				img = self.IMGPATH+"block_not_found.png"
			i = d["id"]
			self.blkdef_images[i] = img
		# Create item textures:
		for i in self.level.get_itemdefs():
			img = self.IMGPATH+"items/"+i+".png"
			if not os.path.exists(img):
				img = self.IMGPATH+"item_not_found.png"
			self.item_images.append(img)
		# Create blocks & items:
		for col in self.level.get_columns():
			x = int(col["position"]*self.blk_sizes[0]/2)
			for blk in col["blocks"]:
				y = self.img_sizes[1]-int((blk["position"]+1)*self.blk_sizes[1]/2)
				bdef = blk["blockdef"]
				img = Image.open(self.blkdef_images[bdef])
				img = img.convert("RGBA")
				img = img.resize(self.blk_sizes, Image.NEAREST)
				self.image.paste(img, (x,y), img)
			for itm in col["items"]:
				y = self.img_sizes[1]-int((itm["position"]+1)*self.blk_sizes[1]/2)
				x += int(self.blk_sizes[1]*0.1)
				iid = itm["id"]
				img = Image.open(self.item_images[iid])
				img = img.convert("RGBA")
				s = int(self.blk_sizes[1]*0.8)
				img = img.resize((s,s), Image.NEAREST)
				self.image.paste(img, (x,y), img)
		# Add text:
		draw = ImageDraw.Draw(self.image)
		s1 = int(self.img_sizes[1]/20)
		s2 = int(self.img_sizes[1]/25)
		s3 = int(self.img_sizes[1]/30)
		font1 = ImageFont.truetype(self.FONTPATH+"Vollkorn-Bold.ttf", s1)
		font2 = ImageFont.truetype(self.FONTPATH+"Vollkorn-Bold.ttf", s2)
		font3 = ImageFont.truetype(self.FONTPATH+"Vollkorn-Regular.ttf", s3)
		draw.text((int(self.img_sizes[1]/30),10), self.level.get_metadata("name"), (0,0,0), font=font1)
		draw.text((int(self.img_sizes[1]/20),20+s1), self.level.get_metadata("creator"), (0,0,0), font=font2)
		draw.text((int(self.img_sizes[1]/15),30+s1+s2), self.level.get_metadata("creator_mail"), (0,0,0), font=font3)
		draw.text((int(self.img_sizes[1]/15),40+s1+s2+s3), self.level.get_metadata("creator_www"), (0,0,0), font=font3)
		# Remove tmpfiles:
		for f in tmpfiles:
			os.unlink(f)
		
	def save(self, path):
		self.image.save(path)

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: %s input.dat output.png" % sys.argv[0], file=sys.stderr)
		sys.exit(1)
	app = ImgGenerator(sys.argv[1])
	app.generate(1080)
	app.save(sys.argv[2])
