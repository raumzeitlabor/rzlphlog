# -*- coding: iso-8859-15 -*-

import sys
import feedparser
import urllib
import html2text
import re
import string
import fnmatch
import os
import argparse
import os.path

FEED = 'https://raumzeitlabor.de/feed/'

ENTRYTEMPLATE = string.Template(
"""== $title ==
pfostiert von $author am $published

$content
""")

GOPHERMAPTEMPLATE = string.Template(
"""          ___                 ____    _ _   ___ _    _
         | _ \__ _ _  _ _ __ |_  /___(_) |_| _ \ |_ | |___  __ _
         |   / _` | || | '  \ / // -_) |  _|  _/ ' \| / _ \/ _` |
         |_|_\__,_|\_,_|_|_|_/___\___|_|\__|_| |_||_|_\___/\__, |
                                                           |___/
                                             Hackerspace Mannheim
                              Digitalkultur im Rhein-Neckar-Kreis

=================================================================
hBesucht uns im WWW	GET /	raumzeitlabor.de	80
=================================================================

$gophermaplines

=================================================================
""")

def normalize(string):
	string = string.replace(u"Ä", "Ae").replace(u"ä", "ae")
	string = string.replace(u"Ö", "Oe").replace(u"ö", "oe")
	string = string.replace(u"Ü", "Ue").replace(u"ü", "ue")
	string = string.replace(u"ß", "ss")
	string = string.encode("ascii", "ignore")
	return string

def create_entry_file(dirname, name, title, published, author, content):
	content = content.rstrip('\r\n')
	d = { "name" : name, "title" : title, "published" : published,
		"author" : author, "content" : content }
	entryfile = os.path.join(dirname, name)
	with open(entryfile, 'w') as file:
		file.write(ENTRYTEMPLATE.substitute(d))

def create_gophermap(dirname, gophermaplines):
	d = { "gophermaplines" : gophermaplines }
	gophermap = os.path.join(dirname, 'gophermap');
	with open(gophermap, 'w') as file:
		file.write(GOPHERMAPTEMPLATE.substitute(d))

def cleanup_entryfiles(dirname, currentfiles):
	for entry in [os.path.join(dirname, entry)
			for entry
			in os.listdir(dirname)
			if fnmatch.fnmatch(entry, "*.phlog")
			and not entry in currentfiles]:
		os.remove(entry)

def create_phlog(feedurl, dirname):
	feed = feedparser.parse(feedurl)
	
	entryfiles = []
	gophermaplines = []
	for entry in feed.entries:
		name = entry.published
		name = re.sub('\W', '_', name)
		name = "{0}.phlog".format(name)
		name = normalize(name)
		title = normalize(entry.title)
		published = normalize(entry.published)
		author = normalize(entry.author)
		text = ""
		for content in [content.value
				for content
				in entry.content
				if content.type == 'text/html']:
			text = normalize(html2text.html2text(content, feedurl))
			break
		if not text:
			text = normalize(html2text.html2text(entry.description))
		create_entry_file(dirname, name, title, published, author, text)
		gophermapline = u"0{0}: {1}\t{2}\t+\t+".format(entry.published,
			entry.title, name)
		gophermaplines.append(normalize(gophermapline))
		entryfiles.append(name)
	create_gophermap(dirname, '\n'.join(gophermaplines))
	cleanup_entryfiles(dirname, entryfiles)

if __name__ == "__main__":
	argparser = argparse.ArgumentParser(
		description='Create a phlog from the RaumZeitLabor feed.')
	argparser.add_argument('--dir', '-d', dest='dir', default=os.getcwd(),
		action='store', help='The target directory')
	args = argparser.parse_args()
	target = os.path.realpath(args.dir)
	create_phlog(FEED, target)

