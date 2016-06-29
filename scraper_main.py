from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import sys
import codecs

def openUrl(url):
	try:
	#try opening url to catch 404 and 500 responses ie link doesn't exist etc
		html = urlopen(url)
	except HTTPError as e:
	#if error occurs, break out
		print(e)
		return None
	except URLError as e:
		print("The server could not be found!")
	else:
		print("It worked!")

	try:
	#try reading content of page into bsObj object for future reference
		bsObj = BeautifulSoup(html.read(), "html.parser")#(html.read(), "lxml")
		#and save title
		title = bsObj.body.h1
	except AttributeError as e:
		return None
	
	#if nothing returns title may be a h2 element, search for that instead below
	if title == None:
		try:
			bsObj = BeautifulSoup(html.read(), "html.parser")#(html.read(), "lxml")
			title = bsObj.body.h2
		except AttributeError as e:
			return None
	print ("Page title is: ", title.get_text())
	
	try:
		#search page for element with content in it's id, that could be site contents 
		#http://www.python-course.eu/python3_exception_handling.php
		article = bsObj.find("", {"id":re.compile("[a-z0-9]*(content)[a-z0-9]*")})
	except AttributeError as e:
		return None
	
	
	#Scrape based on itemprop
	#if article == None:
		#if nothing returns, check for element with class name containing content 
	#	print("First failed.....")
		
	#	#try scraping by itemprop= article
	#	try:
			#https://auth0.com/docs/native-platforms/ionic
	#		print("second running...")
	#		article = bsObj.find("", {"itemprop":re.compile("articleBody")})
	#		print("article found, getting text")
	#		article = article
	#		print("second ran successfully.")
	#	except AttributeError as e:
	#		return None
	

	if article == None:
		#if nothing still, get all content
		print("Second failed.....get whole page")
		try:
			article = bsObj
			#article = bytes(article, "UTF-8")
			#article = article.decode("UTF-8")
		except AttributeError as e:
			return None
	
	#system encoding for US English cp437(default for windows system installation) will vary based on system settings
	print(article.decode('utf-8').encode('cp437', 'replace').decode('cp437'))

#test with: http://news.nationalpost.com/news/world/trump-and-clinton-capture-florida-primary-wins-in-crucial-day-of-voting
def getMetaDescription(bsObj):
	try:
		desc = bsObj.find("meta", {"name": re.compile("(d|D)escription")})["content"]
	except TypeError as e:
		#print("Type error: ", e)
		return getDescription(bsObj)
	except AttributeError as e:
		#print("Attribute Error: Tag was not found")
		return None

	else: 
		if desc == None:
			print("Description tag in meta is empty")
		else: 
			return desc

	#return description for parsing to JSON
	#return desc
	#desc_json = {u"description": desc}
	#new_descObj = json.loads(desc_json)
	#print(json.dumps(desc_json))

#get description based on paragraph of text when meta description fails
def getDescription(bsObj):
	try:
		desc = bsObj.body.p
	except AttributeError as e:
		return None
	else:
		return desc

def getImageUrl(bsObj):
	imageUrl = getImageByOg(bsObj)
	return(imageUrl)

def makeSoup(url):
	try:
		html = urlopen(url)
	except HTTPError as e:
		#print(e)
		return None
	except URLError as e:
		#print("The server could not be found!")
		return None
	#unknown exception
	except:
		#print("Unexpected error occurred")
		return None
		raise

	#no errors on open, go ahead and read
	html = html.read()
	return BeautifulSoup(html, "html.parser")#could be changed to lxml

def getImageByOg(bsObj):
	#find image based on meta containing image in property   
	image = bsObj.find("meta", {"property":re.compile("[a-z0-9A-Z:]*(image)+")})
	if image != None:#extract just valid
		image = image["content"]
	
	if image == None:
		#print("First attempt.....")
		#find image based on meta containing image in name    
		image = bsObj.find("meta", {"name":re.compile("[a-z0-9A-Z:]*(image)+")})
		if image != None:
			image = image["content"]

	if image == None:#find image by tag name 
		#print("second attempt.....")
		image = imageComp(bsObj)


	return image#["content"]

#finds first 3 images on screen
#compares heights of images and returns largest
#TODO: add on fail compare widths or get any picture on the site
def imageComp(bsObj):
	images = bsObj.findAll("img", limit=3)
	height = 0
	for image in images:
		try: 
 			height2 = int(image["height"])#find height of image  via height attribute
 			if height2 > height:
 				height = height2
 				largest = image

		except KeyError as e:
			#print("Error, object doesn't have property: ", e)
			#element doesn't have height property
			#call another function that gets first image and break out of this for loop
			#or set largest to last image already found
			largest = image["src"]
			
	return largest

#get title on page
def getTitle(bsObj):
	titleNotFound = True
	while titleNotFound:
		try:
			title = bsObj.head.title
			break
		except AttributeError as e:
			#print("AttributeError: ", e)
			title = None

		if title == None:
		#this gets executed when page doesn't have title tag in head
		#looks for h1 element 
			try:
				title = bsObj.body.h1
				break
			except AttributeError as e:
				#print("AttributeError: ", e)
				title = None
			#if title not found in h1, check h2
			if title == None:
				#print("H1 cannot be found, searching for H2")
				#try h2
				try:
					title = bsObj.body.h2
					break
				except AttributeError as e:
					#print("AttributeError: ", e)
					title = None
			#if nothing still may have to search for class/id with title
	#return title in text format
	return (title)

#get contents of page without the garbage
def getContent(bsObj):
	try:
		content = bsObj.find("div", {"class":re.compile("[a-z0-9]*(content)[a-z0-9]*")})
	except AttributeError as e:
		content = None

	if content == None:
		try:
			content = bsObj.find("div", {"id":re.compile("[a-z0-9]*(content)[a-z0-9]*")})
		except AttributeError as e:
			content = None

	return (content)

#main method for calling other scripts
#TODO: change expected argument to bsOBJ instead of url to avoid making object repeatedly
def multi(url):
	soup = makeSoup(url)
	url = url
	title = getTitle(soup)
	description = getMetaDescription(soup)
	image = getImageUrl(soup)
	article = getContent(soup)
	toJson(url, title, description, image, article)

#consider refactoring to accept set/list/array whatever
#iterate over it and append to json object
def toJson(url, title, desc, image, article):
	#if imageByOg function returns a value then set flag to true
	#TODO: may have to move to imageByOg function
	if image != None:
		imageByOg = True
	else:
		imageByOg = False
		
	titleFormatted = cleaner(title.get_text())
	descriptionFormatted = cleaner(desc)
	articleFormatted = cleaner(article.get_text())
	#TODO: convert to legit JSON object
	obj = {"url": url, "titleFormatted":titleFormatted, "title": title, "descriptionFormatted": descriptionFormatted, "description": desc, "image": image, "ByOG": imageByOg, "articleFormatted":articleFormatted, "Raw article": article}
	print(obj)

#removes whitespace, newline and other weird characters
def cleaner(strArg):
	strArg = re.sub('\n+', "",strArg)
	strArg = re.sub('\r+', "",strArg)
	strArg = re.sub('\t+', "",strArg)
	strArg = re.sub(' +', " ",strArg)
	return strArg

#https://www.smashingmagazine.com/2015/04/web-scraping-with-nodejs/
#(STRIP OUT NONSENSE IN TITLE ABOVE)
#https://auth0.com/blog/2016/02/22/12-steps-to-a-faster-web-app/
#https://msdn.microsoft.com/en-us/library/system.diagnostics.process(v=vs.110).aspx
#title not in head for link below
#https://cordova.apache.org/docs/en/latest/guide/cli/index.html
#http://news.nationalpost.com/news/world/trump-and-clinton-capture-florida-primary-wins-in-crucial-day-of-voting

#Unicode encoding code
#if sys.stdout.encoding != 'cp65001':
#	sys.stdout = codecs.getwriter('cp65001')(sys.stdout.buffer, 'strict')
#if sys.stderr.encoding != 'cp65001':
#	sys.stderr = codecs.getwriter('cp65001')(sys.stderr.buffer, 'strict')

#print(getContent(makeSoup(str(sys.argv[1]))))
multi(str(sys.argv[1]))