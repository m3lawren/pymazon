#!/usr/bin/python

from xml.dom import minidom, Node
import urllib
import ConfigParser
import sys

def dumpelem(name, element):
	matching = element.getElementsByTagName(name)
	for match in matching:
		if len(match.childNodes) != 1:
			continue
		child = match.firstChild
		if child.nodeType != Node.TEXT_NODE:
			continue
		print name + ': ' + child.nodeValue.strip()

def main():
	config = ConfigParser.SafeConfigParser()
	if config.read('pymazon.conf') == None:
		print 'Unable to read configuration file pymazon.conf'
		sys.exit(1)

	if config.has_option('pymazon', 'AWSAccessKeyId') == False:
		print 'Missing option AWSAccessKeyId in the pymazon section'
		sys.exit(1)

	key = config.get('pymazon', 'AWSAccessKeyId')
	request = 'http://webservices.amazon.com/onca/xml?' + \
	          'Service=AWSECommerceService' + \
				 '&AWSAccessKeyId=' + key + \
				 '&Operation=ItemLookup' + \
				 '&ResponseGroup=ItemAttributes' + \
				 '&ItemId=0618669078'

	file = urllib.urlretrieve(request)[0]
	xmldoc = minidom.parse(file)

	errors = xmldoc.getElementsByTagName('Errors')

	if len(errors) != 0:
		print "Errors occured while executing the request:"

		for error in errors:
			dumpelem('Message', error)

		sys.exit(1)

	dumpelem('Title', xmldoc)
	dumpelem('Author', xmldoc)
	dumpelem('ISBN', xmldoc)
	dumpelem('Edition', xmldoc)
	dumpelem('PublicationDate', xmldoc)
	dumpelem('NumberOfPages', xmldoc)

if __name__ == '__main__':
	main()
	sys.exit(0)
