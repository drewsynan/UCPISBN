""" UCPISBN -- A Module for ISBN-10 and ISBN-13 validation and conversion """

__version__ = "0.0.1"
__date__ = "2014-4-5"
__author__ = "Drew Synan <dsynan@press.uchicago.edu>"
__copyright__ = "Copyright (C) 2014 The University of Chicago Press"
__license__ = "BSD"
__history__ = "See git repository"

import re

__doc__ += """.

"""

class invalidISBN(Exception):
	""" Exception subclass for invalid ISBNs """
	pass

def validate(testISBN):
	"""
	Checks to see if an ISBN string is valid.

	:Parameters:
		testISBN : `str`
			ISBN-10 or ISBN-13 string to validate (with or without hyphens)
	:rtype: `bool`
	:return: Returns True if the ISBN is valid, or raises an invalidISBN exception if not

	"""
	
	testISBN = __stripISBN(testISBN) #strip input of hyphens, periods, and spaces

	if not (len(testISBN) == 10 or len(testISBN) == 13):
		raise invalidISBN("Input not the correct length")

	checkDigit = testISBN[-1].upper()
	trimmed = testISBN[:-1]

	if len(testISBN) == 10:
		if __computeCheck10(trimmed) != checkDigit: raise invalidISBN("Invalid ISBN-10 check digit")

	if len(testISBN) == 13:
		if __computeCheck13(trimmed) != checkDigit: raise invalidISBN("Invalid ISBN-13 check digit")

	return True

def isValidISBN(testISBN):
	""" 
	Checks to see if an ISBN string is valid (does not throw an exception).

	:Parameters:
		testISBN : `str`
	:rtype: `bool`
	:return: Returns True if the testISBN is valid, False if it is not. 

	"""

	try:
		validate(testISBN)
		return True
	except invalidISBN:
		return False

def convert(isbn, prettyPrintResult=False, validateISBN=True):
	"""
	Attempts to convert the input string from 10->13 or 13->10; If an ISBN that is 9 or 12
	digits long is supplied, validation is ignored and the conversion is carried out, regardless of whether
	the validateISBN parameter is True or False.

	:Parameters:
		isbn : `str`
		prettyPrintResult : `bool`
		validateISBN : `bool`
	:rtype: `str`
	:return: Returns converted string. Raises an invalidISBN exception if the input is invalid, contains invalid characters, or is the wrong length. 
	
	"""

	isbn = __stripISBN(isbn)

	if (len(isbn) == 10 or len(isbn) == 9):
		isbnType = "isbn10"
	elif (len(isbn) == 13 or len(isbn) == 12):
		isbnType = "isbn13"
	else:
		raise invalidISBN("Input not long enough to convert")

	if len(isbn) == 9 or len(isbn) == 12: validateISBN = False

	if validateISBN: validate(isbn)

	if isbnType == "isbn10":
		prefixed = "978" + isbn
		if len(prefixed) == 13:
			prefixed = prefixed[:-1]
		converted = prefixed + __computeCheck13(prefixed)
	else:
		chopped = isbn[3:]
		if len(chopped) == 10:
			chopped = chopped[:-1]
		converted = chopped + __computeCheck10(chopped)

	converted = prettyPrintISBN(converted) if prettyPrintResult else converted

	return converted

def getISBN10(isbn, prettyPrintResult=False, validateISBN=True):
	"""
	Returns the ISBN-10 of an input string. Returns the string if it is already a valid ISNB-10. 
	If the input is missing the check digit, validation is skipped, and the ISBN-10 with the
	computed check digit is returned.

	:Parameters:
		isbn : `str`
		prettyPrintResult : `bool`
		validateISBN : `bool`
	:rtype: `str`
	:return: ISBN-10 string

	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 9 or len(isbn) == 12: validateISBN = False

	try:
		if validateISBN: validate(isbn)
	except Exception as e:
		raise invalidISBN("Could not get ISBN-10. Input failed validation: " + str(e))

	if len(isbn) == 10:
		retVal = prettyPrintISBN(isbn) if prettyPrintResult else isbn
	elif len(isbn) == 9:
		retVal = prettyPrintISBN(isbn + getComputedCheckDigit(isbn)) if prettyPrintResult else isbn + getComputedCheckDigit(isbn)
	else:
		retVal = prettyPrintISBN(convert(isbn)) if prettyPrintResult else convert(isbn)

	return retVal

def getISBN13(isbn, prettyPrintResult=False, validateISBN=True):
	"""
	Returns the ISBN-13 for an input string. Returns the string if it is already a valid ISBN-13.
	If the input is mising the check digit, validation is skipped and the ISBN-13 with the
	computed check digit is returned.

	:Parameters:
		isbn : `str`
		prettyPrintResult : `bool`
		validateISBN : `bool`
	:rtype: `str`
	:return: ISBN-13 string

	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 9 or len(isbn) == 12: validateISBN = False

	try:
		if validateISBN: validate(isbn)
	except Exception as e:
		raise invalidISBN("Could not get ISBN-13. Input failed validation: " + str(e))


	if len(isbn) == 10:
		retVal = prettyPrintISBN(convert(isbn)) if prettyPrintResult else convert(isbn)
	elif len(isbn) == 12:
		retVal = prettyPrintISBN(isbn + getComputedCheckDigit(isbn)) if prettyPrintResult else isbn + getComputedCheckDigit(isbn)
	else:
		retVal = prettyPrintISBN(isbn) if prettyPrintResult else isbn

	return retVal


def getBoth(isbn, prettyPrintResult=False, validateISBN=True):
	"""
	Returns both the ISBN-13 and ISBN-10 of an input string. If the input does not have a check digit,
	validation is always skipped and the ISBNs based on computed check digits are returned.
	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 9 or len(isbn) == 12: validateISBN = False

	if validateISBN: validate(isbn)

	both = {'isbn10': getISBN10(isbn, prettyPrintResult), 'isbn13': getISBN13(isbn, prettyPrintResult)}

	return both
def getPrefix(isbn):
	"""
	Gets the EAN prefix from an ISBN-13. Returns an empty string for ISBN-10s

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: EAN prefix string

	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 9 or len(isbn) == 10: return ''
	elif len(isbn) == 12 or len(isbn) == 13: return isbn[0:3]
	else: raise invalidISBN("Input not the correct length to determine prefix")

def getGroupCode(isbn):
	"""
	Gets the language group code for ISBN-10 and ISBN-13s
	Does not (yet) work for 979 non-English ISBNs

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: Language/country group code string

	"""

	isbn = __removePrefix(isbn) # this won't work wtih 979 book codes... should be addressed maybe

	# http://en.wikipedia.org/wiki/List_of_ISBN_identifier_groups
	#

	lower = 'lower'
	upper = 'upper'
	digits = 'digits'

	lookupTable = [
		{lower: 0, upper: 5, digits: 1},
		{lower: 7, upper: 7, digits: 1},
		{lower: 80, upper: 94, digits: 2},
		{lower: 600, upper: 649, digits: 3},
		{lower: 950, upper: 989, digits: 3},
		{lower: 9900, upper: 9989, digits: 4},
		{lower: 99900, upper: 99999, digits: 5}
	]

	for groupCode in lookupTable:
		testSubstring = isbn[0:groupCode['digits']]
		if int(testSubstring) >= groupCode['lower'] and int(testSubstring) <= groupCode['upper']: return testSubstring

	raise invalidISBN("Could not determine group code. Malformed ISBN?")


def getPublisherCode(isbn):
	"""
	Gets the varying-digit publisher code for English language publishers for both
	ISBN-10 and ISBN-13s

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: Publisher code string

	"""

	groupCode = getGroupCode(isbn)
	isbn = __removePrefix(isbn)[1:] #use prefixless isbn with group code removed

	lower = 'lower'
	upper = 'upper'
	digits = 'digits'

	lookupTable = {
		"0": [ #GROUP 0
			{lower: 0, upper: 19, digits: 2},
			{lower: 200, upper: 699, digits: 3},
			{lower: 7000, upper: 8499, digits: 4},
			{lower: 85000, upper: 89999, digits: 5},
			{lower: 900000, upper: 949999, digits: 6},
			{lower: 9500000, upper: 9999999, digits: 7}
		],
		"1": [ #GROUP 1
			{lower: 0, upper: 9, digits: 2},
			{lower: 100, upper: 399, digits: 3},
			{lower: 4000, upper: 5499, digits: 4},
			{lower: 55000, upper: 86979, digits: 5},
			{lower: 869800, upper: 998999, digits: 6},
			{lower: 9990000, upper: 9999999, digits: 7}
		]
	}

	try:
		for publisherGroup in lookupTable[groupCode]:
			testSubstring = isbn[0:publisherGroup['digits']]
			if int(testSubstring) >= publisherGroup['lower'] and int(testSubstring) <= publisherGroup['upper']: return testSubstring

	except KeyError:
		raise Exception("Publisher lookup tables for non-English languages not yet implemented")
	except Exception as e: #Other Error
		print e
		raise e

def getItemCode(isbn):
	"""
	Gets the item code for an ISBN-10 or ISBN-13

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: Item code string

	"""

	isbn = __stripISBN(isbn)

	prefixLength = len(getPrefix(isbn))
	groupLength = len(getGroupCode(isbn))
	publisherLength = len(getPublisherCode(isbn))

	offset = prefixLength + groupLength + publisherLength

	if len(isbn) == 9 or len(isbn) == 12:
		return isbn[offset:]
	else:
		return isbn[offset:-1]

def getInputCheckDigit(isbn):
	"""
	Gets the check digit from the supplied ISBN parameter. If the check digit cannot be determined, 
	raises an invalidISBN exception. DOES NOT validate or calculate the check digit.

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: Check digit from input ISBN (does not validate)
	"""

	isbn = __stripISBN(isbn)

	if not (len(isbn) == 10 or len(isbn) == 13):
		raise invalidISBN("Input not the right length to find check digit")

	else: return isbn[-1]

def getComputedCheckDigit(isbn):
	"""
	Returns the computed check digit for the intered ISBN string.
	If the input is 9 or 10 characters long the input is assumed to be an ISBN-10
	if the input is 12 or 13 characters long the input is assumed to be an ISBN-13
	Raises an invalidISBN exception if the ISBN type cannot be determined from the input length

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: Check digit string calculated from the given ISBN.

	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 10 or len(isbn) == 9:
		return __computeCheck10(isbn)
	elif len(isbn) == 13 or len(isbn) == 12:
		return __computeCheck13(isbn)
	else:
		raise invalidISBN("Input not the right length to calculate check digit")

def getTrimmedInput(isbn):
	"""
	Returns the input ISBN string with its check digit removed

	:Parameters:
		isbn : `str`
	:rtype: `str`
	:return: ISBN string with check digit removed

	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 9 or len(isbn) == 12:
		return isbn
	elif len(isbn) == 10 or len(isbn) == 13:
		return isbn[:-1]
	else:
		raise invalidISBN("Input not the right length to remove check digit")

def __removePrefix(isbn):
	""" 
	(Private) Removes the bookland prefix from an ISBN-13, returns an ISBN-10 unaltered. Does not alter
	the check digit.
	"""

	isbn = __stripISBN(isbn)

	if len(isbn) == 13 or len(isbn) == 12:
		split = isbn.split("978")
		if len(split) != 2: raise invalidISBN("Not a valid bookland 978 prefix. This utility does not work on 979 prefixes")
		else: 
			isbn = split[1]
	if len(isbn) == 9 or len(isbn) == 10:
		isbn = isbn
	else:
		raise invalidISBN("Input is not the correct length")

	return isbn

def __stripISBN(isbn):
	""" 
	Checks for invalid characters, then removes hyphens, periods and spaces from an input string.
	"""

	noPunc = re.sub('[-. ]', '', str(isbn).upper())

	allowedChars = ["0","1","2","3","4","5","6","7","8","9"]
	if len(noPunc) == 10: allowedChars.append("X")

	for char in noPunc:
		if char not in allowedChars: raise invalidISBN("ISBN contains invalid characters")

	return noPunc

def __computeCheck13(isbn):
	""" Returns the ISBN-13 check digit from an input string of 12 or 13 characters """

	isbn = __stripISBN(isbn) #strip input of hyphens, periods, and spaces

	if not (len(isbn) == 13 or len(isbn) == 12):
		raise invalidISBN("Input not the right length to compute ISBN-13 check digit")

	if len(isbn) == 13:
		trimmed = isbn[:-1]
	else:
		trimmed = isbn

	sum = 0
	for i in range(len(trimmed)):
		c = int(trimmed[i])
		if i % 2: w = 3
		else: w = 1
		sum += w * c

	checkDigit = (10 - (sum % 10)) % 10

	return str(checkDigit)

def __computeCheck10(isbn):
	""" Returns the ISBN-10 check digit from in input string of 9 or 10 characters """

	isbn = __stripISBN(isbn) #strip input of hyphens, periods, and spaces

	if not (len(isbn) == 9 or len(isbn) == 10):
		raise invalidISBN("Input not the right length to compute ISBN-10 check digit")

	if len(isbn) == 10:
		trimmed = isbn[:-1]
	else:
		trimmed = isbn

	checkDigit = 0
	multiplier = 10
	#compute testCheck for isbn10
	for digit in trimmed:
		checkDigit = checkDigit + multiplier * int(digit)
		multiplier = multiplier - 1

	checkDigit = (11 - (checkDigit % 11)) % 11

	if checkDigit == 10:
		checkDigit = "X"

	return str(checkDigit)

def prettyPrint(isbn):
	""" Alias for prettyPrintISBN """
	return prettyPrintISBN(isbn)

def prettyPrintISBN(isbn):
	""" Returns a pretty printed string with hyphens of an ISBN-10 or ISBN-13 """

	isbn = __stripISBN(isbn) #strip input of hyphens, periods, and spaces
	
	if not (len(isbn) == 10 or len(isbn) == 13):
		raise invalidISBN("Cannot pretty print; invalid ISBN length")

	try:
		prettyPrefix = ''
		if getPrefix(isbn) != '': prettyPrefix = getPrefix(isbn) + "-"

		prettyString = prettyPrefix + getGroupCode(isbn) + "-" + getPublisherCode(isbn) + "-" + getItemCode(isbn) + "-" + getInputCheckDigit(isbn)
	
	except: #Still return something even if not in a 0 or 1 group
		prettyString = isbn

	return prettyString

