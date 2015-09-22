# -*- coding: iso-8859-15 -*-

import icalendar
import urllib
import argparse
import string
import os.path
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

ICAL = 'https://raumzeitlabor.de/events.ics'

GOPHERMAPTEMPLATE = string.Template(
"""        ___                 ____    _ _   ___             _      
       | _ \__ _ _  _ _ __ |_  /___(_) |_| __|_ _____ _ _| |_ ___
       |   / _` | || | '  \ / // -_) |  _| _|\ V / -_) ' \  _(_-<
       |_|_\__,_|\_,_|_|_|_/___\___|_|\__|___|\_/\___|_||_\__/__/

                                             Hackerspace Mannheim
                              Digitalkultur im Rhein-Neckar-Kreis

=================================================================
hRaumZeitEvents im WWW	GET /	was.geht.im.rzl.so	80
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

def get_calendar(ical):
	u = urllib.urlopen(ical)
	t = u.read()
	u.close()
	c = icalendar.Calendar().from_ical(t)
	return c

def create_gophermap(dirname, gophermaplines):
	d = { 'gophermaplines': gophermaplines }
	gophermap = os.path.join(dirname, 'gophermap')
	with open(gophermap, 'w') as file:
		file.write(GOPHERMAPTEMPLATE.substitute(d))

gophermaplines = []
def create_events(ical, dirname):
	lastmonth = None
	lastyear = None
	for c in get_calendar(ical).walk(name='VEVENT'):
		sd = icalendar.prop.vDDDTypes.from_ical(c['DTSTART'])
		if lastmonth != sd.month or lastyear != sd.year:
			lastmonth = sd.month
			lastyear = sd.year
			gophermaplines.append('')
			gophermaplines.append(sd.strftime('%B %Y'))
			gophermaplines.append('')
		ed = icalendar.prop.vDDDTypes.from_ical(c['DTEND'])
		summary = c['SUMMARY'].split(' - ')[0]
		gophermaplines.append('{0} - {1}: {2}'.format(
			sd.strftime('%a, %d.%m. %H:%M'),
			ed.strftime('%a, %d.%m. %H:%M'),
			normalize(summary)))
		create_gophermap(dirname, '\n'.join(gophermaplines))

if __name__ == '__main__':
	argparser = argparse.ArgumentParser(
		description='Create a gophermap from the RaumZeitLabor ical ' +
		'feed.')
	argparser.add_argument('--dir', '-d', dest='dir', default=os.getcwd(),
		action='store', help='The target directory')
	args = argparser.parse_args()
	target = os.path.realpath(args.dir)
	create_events(ICAL, target)
