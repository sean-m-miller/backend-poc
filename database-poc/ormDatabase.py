import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
# Creating a local SQLite database (Stored in memory)
# If echo=True then sqlalchemy will log, else it wont
engine = create_engine('sqlite:///:memory:', echo=False)

# Definition of base object class
Base = declarative_base()

class User(Base):
	"""Represents a user in our database.

	The User object stores information about the user along with
	the books that they have posted.

    Attributes:
        id (int): A UUID generated automatically when a user is added.
        fullname (str): The fullname of the user.
        classYear (int): The classyear of the user (0-4).
        books (Book[]): A list of books posted by the user.

    """

    # Required by SQLalchemy to create tables
	__tablename__ = 'users'

	# User data
	id = Column(Integer, primary_key=True)
 	# Some SQL management systems allow generation without length
 	# others require a length. Syntax: Column(String(50))
	fullname = Column(String)
	classYear = Column(Integer)
	books = relationship("Book", order_by="Book.listingID", back_populates="user", cascade="all, delete, delete-orphan")

	# For debugging, how class will print
	def __repr__(self):
		return "<User(id='%s', fullname='%s', classYear='%s', books='%s')>" % (
			self.id, self.fullname, self.classYear, self.books)

class Book(Base):
	"""The Book object stores information about the book listing.

    Attributes:
        listingID (int): A unique id, automatically generated.
        isbn (str): The book ISBN.
        title (str): The book title.
        author (str): The book author.
        price (int): The price being asked for the book.
        user_id (int): The UUID of the user who posted the book.
        user (User): The User object of the student who posted the book.
    """

    # Required by SQLalchemy to create tables
	__tablename__ = 'books'

	# Book data
	# Listing id will automatically be generated when book is added to database
	listingID = Column(Integer, primary_key=True)
	isbn = Column(String)
	title = Column(String)
	author = Column(String)
	price = Column(Integer)
	# books.user_id should be constrained to values in users.id
	user_id = Column(Integer, ForeignKey('users.id'))
	# Create a relationship to the user
	user = relationship("User", back_populates="books", cascade="all, delete")

	# For debugging, how class will print
	def __repr__(self):
		return "<Book(listingID='%s', isbn='%s', title='%s', author='%s', price='%s', user='%s')>" % (
			self.listingID, self.isbn, self.title, self.author, self.price, self.user.fullname)

# Create a table for user objects
User.__table__
Book.__table__

# Generate all tables
Base.metadata.create_all(engine)

# Create a session maker to create Session objects
Session = sessionmaker(bind=engine)
# Instantiate a session to communicate with the database
session = Session()


"""Database Functions

Many of these functions are not neccesary for the database to function,
but provide abstraction from the SQLalchemy functions.

At the very least, they provide examples of the SQLalchemy syntax
to perform certain database tasks.
"""

# ===== User Functions =====
def CreateUser(id, fullname, classYear):
	"""Create a user object.

	Args:
		id (int): User (Whitman) ID
		fullname (str): Full name of user
		classYear (int): Class year of user

	Returns:
		User: User object
	"""
	return User(id=id, fullname=fullname, classYear=classYear)

# Add user to database
def AddUser(user):
	"""Adds a user to the user table (database).

	Args:
		user (User): The user to be added to the table

	Returns:
		none
	"""
	session.add(user)

def FindUser(id):
	"""Get the user object related by user id.

	Args:
		id (int): The user id to query with.

	Returns:
		User: The user related to the user id.
	"""
	return session.query(User).filter_by(id=id).first()

def FindUserByName(name):
	"""Get a list of the users with a certain name.

	Args:
		name (str): The name to search for

	Returns:
		User[]: A list of users with a certain name.
	"""
	return session.query(User).filter_by(fullname=name).all()

# Return a list of all users sorted by user id
def ListUsers():
	"""Get a list of all users, sorted by user id.

	Args:
		none

	Returns:
		User[]: A list of all users, by user id.
	"""
	return session.query(User).order_by(User.id).all()

def ListUsersByName():
	"""Get a list of all users, sorted by name.

	Args:
		none

	Returns:
		User[]: A list of all users, by name.
	"""
	return session.query(User).order_by(User.fullname).all()
 
def ListUsersInClass(classYear):
	"""Get a list of all users in a certain class year.

	Perhaps not useful for our case, but if we kept track of classes
	that each user were taken then it may be interesting to sort
	by the classes they are taking. (To clarify, this function is
	for class year).

	Args:
		classYear (int): The class year to search for

	Returns:
		User[]: A list of all users in a class year.
	"""
	return session.query(User).filter_by(classYear=classYear).all()

# ===== Book Functions =====
# Create a book instance
def CreateBook(isbn, title, author, price, user):
	"""Create a book instance.

	Args:
		isbn (str): The book's ISBN.
		title (str): The book title.
		author (str): The author of the book.
		price (int): The price asked for by the user.
		user (User): The user who posted the book.

	Returns:
		Book: The book object that was created.
	"""
	return Book(isbn=isbn, title=title, author=author, price=price, user=user)

def AddBook(book):
	"""Add a book to the book table (database).

	Args:
		book (Book): The book to be added to the database.

	Returns:
		none.
	"""
	session.add(book)

def RemoveBook(book):
	"""Remove a book from the database.

	Args:
		book (Book): The book to be removed from the database.

	Returns:
		none.
	"""
	session.delete(book)

def SearchFor(searchString):
	"""Search for a book in the database (Currently only by title).

	Args:
		searchString (str): The user inputted search string.

	Returns:
		Book[]: A list of books that match the sort result.
	"""
	return session.query(Book).filter(Book.title.like('%'+searchString+'%')).all()

def FindBooksWithISBN(isbn):
	"""Get a list of all books with a given isbn.

	Multiple identical books may exist with the same isbn,
	as we are treating all books as entries.

	Args:
		isbn (str): The isbn to match with books.

	Returns:
		Book[]: A list of books that match the isbn.
	"""
	return session.query(Book).filter_by(isbn=isbn).all()

def FindBookByTitle(title):
	"""Get a list of all books with a given title.

	Multiple identical books may exist with the same title,
	as we are treating all books as entries.

	Args:
		title (str): The title of the book.

	Returns:
		Book[]: A list of books that match the isbn.
	"""
	return session.query(Book).filter_by(title=title).first()

def ListBooks():
	"""Get a list of all books, sorted by title.

	Args:
		none.

	Returns:
		Book[]: A list of all books in the table.
	"""
	return session.query(Book).order_by(Book.title).all()

def ListBooksByAuthor():
	"""Get a list of all books, sorted by author.

	Args:
		none.

	Returns:
		Book[]: A list of all books in the table.
	"""
	return session.query(Book).order_by(Book.author).all()

def ListBooksByISBN():
	"""Get a list of all books, sorted by ISBN.

	Args:
		none.

	Returns:
		Book[]: A list of all books in the table.
	"""
	return session.query(Book).order_by(Book.isbn).all()

def ListBooksFromAuthor(author):
	"""Get a list of all books by a certain author.

	Args:
		author (str): The author to search for.

	Returns:
		Book[]: A list of all books in the table with a given author.
	"""
	return session.query(Book).filter_by(author=author).all()

def ListBooksFromUser(user):
	"""Get a list of all books posted by a certain user.

	Args:
		user (str): The user to search for.

	Returns:
		Book[]: A list of all books in the table posted by a certain user.
	"""
	return session.query(Book).filter_by(user=user).all()

# ===== Misc Functions =====
def PrintList(list):
	"""Print a list, line by line.

	Args:
		list (list): The list to be printed

	Returns:
		none.
	"""
	for item in list:
		print(item)
		print()

def PopTables():
	"""Populate the database tables with test data.

	Args:
		none.

	Returns:
		none.
	"""
	AddUser(CreateUser(1111, "Wayne Gretsky", 4))
	AddUser(CreateUser(2222, "Sidney Crosby", 3))
	AddUser(CreateUser(3333, "Brock Boeser", 1))
	AddUser(CreateUser(4444, "Daniel Sedin", 3))
	AddUser(CreateUser(5555, "Ryan Getslaf", 2))

	AddBook(CreateBook("1610020243", "Textbook of Neonatal Resuscitation", "Gary M Weiner", 80, FindUser(1111)))
	AddBook(CreateBook("1118324579", "Materials Science and Engineering: An Introduction", "William D. Callister Jr.", 90, FindUser(3333)))
	AddBook(CreateBook("0321616677", "Evolutionary Analysis", "Jon. C Herron", 110, FindUser(4444)))
	AddBook(CreateBook("0321907981", "Technical Communication Today", "Richard Johnson-Sheehan", 70, FindUser(2222)))
	AddBook(CreateBook("1285852702", "Delmar's Standard Textbook of Electricity", "Stephen Herman", 60, FindUser(5555)))
	AddBook(CreateBook("0323319742", "Mosby's Textbook for Nursing Assistants", "Sheila A. Sorrentino", 140, FindUser(1111)))
	AddBook(CreateBook("0138147574", "Signals and Systems", "Alan V. Oppenheim", 120,  FindUser(2222)))
	AddBook(CreateBook("1848726953", "Textbook of Clinical Neuropsychology", "Joel E. Morgan", 100, FindUser(4444)))

def ClearTables():
	"""Clear both user and book tables.

	Args:
		none.

	Returns:
		none.
	"""
	session.query(User).delete()
	session.query(Book).delete()



