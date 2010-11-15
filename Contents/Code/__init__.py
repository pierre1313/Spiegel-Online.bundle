# -*- coding: utf-8 -*-
'''
Created on November 12, 2010

Version: 0.1
Author: by Pierre
'''

# Plugin parameters
PLUGIN_TITLE = "Spiegel Online"
PLUGIN_PREFIX = "/video/spiegel"

# Art
ICON = "icon-default.png"
ART = "art-default.jpg"
PREFS = "icon-prefs.png"

#Some URLs for the script
CATEGORY_URL = "http://www1.spiegel.de/active/playlist/fcgi/playlist.fcgi/asset=flashvideo/mode=list/displaycategory=%s/count=%s/start="
FEATURED_URL = "http://www1.spiegel.de/active/playlist/fcgi/playlist.fcgi/asset=flashvideo/mode=%s"
VIDEOXML_URL = "http://video.spiegel.de/flash/%s.xml"
VIDEOFILE_URL = "http://video.spiegel.de/flash/%s"

Categories = [("aktuell2","Aktuell"),("newsmitfragmenten","News"),("politikundwirtschaft","Politik & Wirtschaft"),("panorama2","Panorama"),("kino","Kino"),("kultur","Kultur"),("sport2","Sport"),("wissenundtechnik","Wissen & Technik"),("blogs","Serien & Blogs"),("spiegel%20tv%20magazin","SPIEGEL TV Magazin")]

####################################################################################################

def Start():
	# Register our plugins request handler
	Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, ICON, ART)
	
	# Add in the views our plugin will support
	
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	
	# Set up our plugin's container
	
	MediaContainer.title1 = PLUGIN_TITLE
	MediaContainer.viewGroup = "List"
	MediaContainer.art = R(ART)
	DirectoryItem.thumb = R(ICON)
	
	# Configure HTTP Cache lifetime
	
	HTTP.CacheTime = 3600

####################################################################################################
# The plugin's main menu. 

def MainMenu():

	dir = MediaContainer(art = R(ART), viewGroup = "List")
	dir.Append(Function(DirectoryItem(AllVideos, title="Alle Videos", thumb=R(ICON) )))
	dir.Append(Function(DirectoryItem(ParseCategoryXML, title="Am meisten angesehen", thumb=R(ICON)),title = "Am meisten angesehen", link = (FEATURED_URL%"toptwentyseen"), page = 0))
	dir.Append(Function(DirectoryItem(ParseCategoryXML, title="Am meisten verschikt", thumb=R(ICON)),title = "Am meisten verschikt", link = (FEATURED_URL%"toptwenty"), page = 0))
	dir.Append(PrefsItem(title="Einstellungen",subtile="",summary="Einstellungen",thumb=R(PREFS)))

	return dir
    
def AllVideos(sender):
	dir = MediaContainer(art = R(ART), viewGroup = "List")
	for category in Categories:
		dir.Append(Function(DirectoryItem(ParseCategoryXML, title=category[1], thumb=R(ICON)),title = category[1], link = (CATEGORY_URL%(category[0],Prefs['Videosperpage'])), page = 1))

	return dir

####################################################################################################

def GetThumb(path,thumb_type = "image/jpg"):
	if (path == None):
		return R(ICON)
	image = HTTP.Request(path).content
	return DataObject(image,thumb_type) 	

def ParseCategoryXML(sender, title, link, page):
	dir = MediaContainer(art = R(ART), viewGroup = "InfoList", title2 = title, replaceParent = (page>1))
	
	if page>0:
		locallink = link + str(int(Prefs['Videosperpage'])*(page-1)+1)
		Log(locallink)
	else:
		locallink = link

	xmlfeed = XML.ElementFromURL(locallink,encoding = "iso-8859-1")
	
	if (page>1):
		dir.Append(Function(DirectoryItem(ParseCategoryXML, title="Previous Zeite"),title =title, link = link , page = page - 1))
	
	for video in xmlfeed.xpath("//playlist/listitem"):
		id = video.xpath("videoid")[0].text
		title = video.xpath("headline")[0].text.encode("utf-8")
		try:
  		  summary = video.xpath("teaser")[0].text.encode("utf-8")
		except: 
		  summary = HTML.StringFromElement(video,encoding = "iso-8859-1")
  		  summary = summary[summary.find('<teaser>')+8:]
		  summary = summary[:summary.find('<')].encode("utf-8")

		try: 
		  thumbpath = video.xpath("thumb")[0].text
		except: 
		  thumbpath = ''

		if Prefs['ShowAllRes'] == "Alle" :
			dir.Append(Function(DirectoryItem(ParseVideoXML, title=title, summary = summary, thumb=Function(GetThumb,path = thumbpath)),title =title, summary = summary, thumbpath = thumbpath, link = (VIDEOXML_URL%id)))
		else:
			maxres = 0
			url = None	
			xmlfeed = XML.ElementFromURL((VIDEOXML_URL%id),encoding = "iso-8859-1")
			for streams in xmlfeed.xpath("//encodings"):
				for stream in streams:
					filename = stream.xpath("filename")[0].text
					extension = filename[filename.find('.')+1:]

					if (extension=="mp4" or extension=="flv"):
						currentres = int(stream.xpath("width")[0].text) + int(stream.xpath("height")[0].text)
						if (currentres >= maxres):
							maxres = currentres
							url = VIDEOFILE_URL % stream.xpath("filename")[0].text
			if (url != None):
				dir.Append(VideoItem(url, title=title, summary=summary, thumb=Function(GetThumb,path=thumbpath))) 

	if (page>0):
		#nextpage = ("Nächste Seite").decode("iso-8859-1").encode("utf-8")
		dir.Append(Function(DirectoryItem(ParseCategoryXML, title="Nächste Seite"),title = title, link = link , page = page + 1)) #ä
	return dir     

def ParseVideoXML(sender, title, summary, thumbpath, link):
	dir = MediaContainer(art = R(ART), viewGroup = "List", title2 = title)
	Log(link)
	xmlfeed = XML.ElementFromURL(link,encoding = "iso-8859-1")

	for streams in xmlfeed.xpath("//encodings"):
		for stream in streams:
			width = stream.xpath("width")[0].text
			height = stream.xpath("height")[0].text
			filename = stream.xpath("filename")[0].text

			url = VIDEOFILE_URL % filename
			extension = filename[filename.find('.')+1:]
			thistitle = title + " - " + width + "x" + height + " - " + extension
			if (extension=="mp4" or extension=="flv"):
				dir.Append(VideoItem(url, title=thistitle, summary=summary, thumb=Function(GetThumb,path=thumbpath))) 
	return dir