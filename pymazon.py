#!/usr/bin/python

from xml.dom import minidom, Node
import urllib
import ConfigParser
import sys

class PyMazonError(StandardError):
	"""Holds information about an error that occured during a pymazon request"""
	def __init__(self, messages):
		self.__message = '\n'.join(messages)

	def __get_message(self):
		return self.__message

	def __str__(self):
		return repr(self.__message)

	message = property(fget=__get_message)


class PyMazonBook:
	"""Stores information about a book retrieved via PyMazon."""
	def __init__(self, title, authors, isbn10, isbn13, edition):
		self.__title = title
		self.__authors = authors
		self.__isbn10 = isbn10
		self.__isbn13 = isbn13
		self.__edition = edition

	def __str__(self):
		return 'Title:     ' + self.__title + '\n' + \
		       'Author(s): ' + ', '.join(self.__authors) + '\n' \
				 'ISBN-10:   ' + self.__isbn10 + '\n' + \
				 'ISBN-13:   ' + self.__isbn13 + '\n' + \
				 'Edition:   ' + self.__edition

	def __get_title(self):
		return self.__title

	def __get_authors(self):
		return self.__authors

	def __get_isbn10(self):
		return self.__isbn10

	def __get_isbn13(self):
		return self.__isbn13

	def __get_edition(self):
		return self.__edition

	title = property(fget=__get_title)
	authors = property(fget=__get_authors)
	isbn10 = property(fget=__get_isbn10)
	isbn13 = property(fget=__get_isbn13)
	edition = property(fget=__get_edition)


class PyMazon:
	"""A method of looking up book information on Amazon."""
	def __init__(self, accesskey):
		self.__key = accesskey

	def __form_request(self, isbn):
		return 'http://webservices.amazon.com/onca/xml?' + \
		       'Service=AWSECommerceService' + \
		       '&AWSAccessKeyId=' + self.__key + \
				 '&Operation=ItemLookup' + \
				 '&ResponseGroup=ItemAttributes' + \
				 '&IdType=ISBN' + \
				 '&SearchIndex=Books' + \
				 '&ItemId=' + isbn

	def __elements_text(self, element, name):
		result = []
		matching = element.getElementsByTagName(name)
		for match in matching:
			if len(match.childNodes) != 1:
				continue
			child = match.firstChild
			if child.nodeType != Node.TEXT_NODE:
				continue
			result.append(child.nodeValue.strip())
		return result

	def __format_errors(self, errors):
		error_list = []
		for error in errors:
			error_list.extend(self.__elements_text(error, 'Message'))
		return error_list

	def __extract_single(self, element, name):
		matches = self.__elements_text(element, name)
		if len(matches) == 0:
			return ''
		return matches[0]

	def lookup(self, isbn):
		file = urllib.urlretrieve(self.__form_request(isbn))[0]
		xmldoc = minidom.parse(file)

		errors = xmldoc.getElementsByTagName('Errors')
		if len(errors) != 0:
			raise PyMazonError, self.__format_errors(errors)

		title = self.__extract_single(xmldoc, 'Title')
		authors = self.__elements_text(xmldoc, 'Author')
		isbn10 = self.__extract_single(xmldoc, 'ISBN')
		isbn13 = self.__extract_single(xmldoc, 'EAN')
		edition = self.__extract_single(xmldoc, 'Edition')

		return PyMazonBook(title, authors, isbn10, isbn13, edition)

def main():
	config = ConfigParser.SafeConfigParser()
	if config.read('pymazon.conf') == None:
		print 'Unable to read configuration file pymazon.conf'
		sys.exit(1)

	if config.has_option('pymazon', 'AWSAccessKeyId') == False:
		print 'Missing option AWSAccessKeyId in the pymazon section'
		sys.exit(1)

	key = config.get('pymazon', 'AWSAccessKeyId')

	pymazon = PyMazon(key)
	print pymazon.lookup('9780618669073')
	print pymazon.lookup('0618669078')

if __name__ == '__main__':
	main()
	sys.exit(0)
