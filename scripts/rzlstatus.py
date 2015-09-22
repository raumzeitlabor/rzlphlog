# -*- coding: iso-8859-15 -*-

import urllib
import string
import argparse
import os.path
import json
import datetime
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

STATUSURI = 'https://status.raumzeitlabor.de/api/full.json'

GOPHERMAPTEMPLATE = string.Template(
"""      ___                 ____    _ _   ___ _        _
     | _ \__ _ _  _ _ __ |_  /___(_) |_/ __| |_ __ _| |_ _  _ ___
     |   / _` | || | '  \ / // -_) |  _\__ \  _/ _` |  _| || (_-<
     |_|_\__,_|\_,_|_|_|_/___\___|_|\__|___/\__\__,_|\__|\_,_/__/
                                             Hackerspace Mannheim
                              Digitalkultur im Rhein-Neckar-Kreis

=================================================================
hDer RaumZeitStatus im WWW	GET /	status.raumzeitlabor.de	80
=================================================================

Das RaumZeitLabor ist $tuer und $geraete Geraete sind aktiv.

Identifizierte kohlenstoffbasierte Lebensformen:

$laboranten

                    ($datetime)
=================================================================
""")

def normalize(string):
	string = string.replace(u"Ä", "Ae").replace(u"ä", "ae")
	string = string.replace(u"Ö", "Oe").replace(u"ö", "oe")
	string = string.replace(u"Ü", "Ue").replace(u"ü", "ue")
	string = string.replace(u"ß", "ss")
	string = string.encode("ascii", "ignore")
	return string

def create_gophermap(dirname, json):
	tuer = "unbekannt"
	if json['details']['tuer'] == '1':
		tuer = "offen"
	elif json['details']['tuer'] == '0':
		tuer = "geschlossen"

	laboranten = json['details']['laboranten']
	if len(laboranten) > 0:
		laboranten.sort()
	else:
		laboranten.add("(niemand)")

	d = { 'tuer' : tuer,
		'geraete' : json['details']['geraete'],
		'laboranten' : '\n'.join('    {0}'.format(name)
				for name in laboranten),
		'datetime' : datetime.datetime.now().strftime('%c')
		}
	gophermap = os.path.join(dirname, 'gophermap')
	with open(gophermap, 'w') as file:
		file.write(GOPHERMAPTEMPLATE.substitute(d))

def get_json(uri):
	u = urllib.urlopen(uri)
	j = u.read()
	u.close()
	return json.loads(j)

if __name__ == '__main__':
	argparser = argparse.ArgumentParser(
		description='Create a phlog from the RaumZeitLabor feed.')
	argparser.add_argument('--dir', '-d', dest='dir', default=os.getcwd(),
		action='store', help='The target directory')
	args = argparser.parse_args()
	target = os.path.realpath(args.dir)
	create_gophermap(target, get_json(STATUSURI))

