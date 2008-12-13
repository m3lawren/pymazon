#!/usr/bin/python

from pymazon import PyMazon
import pgdb as dbapi2
import ConfigParser
import sys

def getoption(config, section, name):
	if config.has_option(section, name) == False:
		sys.stderr.write('Missing option ' + name + ' in section ' + section + '\n')
		sys.exit(1)
	return config.get(section, name)	

def main():
	config = ConfigParser.SafeConfigParser()
	if config.read('pymazon.conf') == None:
		print 'Unable to read configuration file pymazon.conf'
		sys.exit(1)

	key = getoption(config, 'pymazon', 'AWSAccessKeyId')
	pg_dbname = getoption(config, 'postgres', 'dbname')
	pg_username = getoption(config, 'postgres', 'username')
	pg_password = getoption(config, 'postgres', 'password')
	pg_host = getoption(config, 'postgres', 'host')

	db = dbapi2.connect(database=pg_dbname, host=pg_host, user=pg_username, password=pg_password)
	cur = db.cursor()

	pymazon = PyMazon(key)

	while True:
		sys.stdout.write('isbn> ')

		isbn = sys.stdin.readline()
		if isbn == '' or isbn == 'quit\n':
			break
		isbn = isbn.strip()

		try:
			book = pymazon.lookup(isbn)
		except PyMazonError, e:
			sys.stderr.write('Error: ' + e.message + '\n')
			continue

		data = {'isbn': isbn, \
		        'title': book.title, \
				  'authors': ', '.join(book.authors), \
				  'year': book.year, \
				  'edition': book.edition, \
				  'publisher': book.publisher}
		print book.__str__().encode('utf_8')
		
		cur.execute("SELECT isbn FROM books WHERE isbn=%s;", (isbn,))
		result = cur.fetchall()
		if len(result) == 0:
			sys.stdout.write('Adding book into the database...')
			cur.execute("""
				INSERT INTO books(isbn, title, authors, year, edition, publisher)
				VALUES (%s, %s, %s, %s, %s, %s);
				""", (isbn, book.title, ', '.join(book.authors), book.year, book.edition, book.publisher))
			sys.stdout.write('OK\n')
			db.commit()
		else:
			sys.stdout.write('Book already exists in the database, updating information...')
			cur.execute("""
			   UPDATE books 
				SET title=%s, 
				    authors=%s, 
					 year=%s, 
					 edition=%s, 
					 publisher=%s 
				WHERE isbn=%s
				""", (book.title, ', '.join(book.authors), book.year, book.edition, book.publisher, isbn))
			sys.stdout.write(' OK\n')
			db.commit()

if __name__ == '__main__':
	main()
	sys.exit(0)
