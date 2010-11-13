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

#Some URLs for the script
CATEGORY_URL = "http://www1.spiegel.de/active/playlist/fcgi/playlist.fcgi/asset=flashvideo/mode=list/displaycategory=%s/count=10/start="
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
	for category in Categories:
	  dir.Append(Function(DirectoryItem(ParseCategoryXML, title=category[1], thumb=R(ICON)),title = category[0], link = (CATEGORY_URL%category[0]), page = 1))
		 
	return dir

####################################################################################################

def GetThumb(path,thumb_type = "image/jpg"):
    if (path == None):
      return R(ICON)
    image = HTTP.Request(path).content
    return DataObject(image,thumb_type) 	
	
def ParseCategoryXML(sender, title, link, page):
	dir = MediaContainer(art = R(ART), viewGroup = "InfoList", title2 = title, replaceParent = (page>1))
	locallink = link + str(10*(page-1)+1)
	Log(locallink)
	xmlfeed = HTML.ElementFromURL(locallink,encoding = "iso-8859-1")
	
	if (page>1):
		dir.Append(Function(DirectoryItem(ParseCategoryXML, title="Previous Zeite"),title =title, link = link , page = page - 1))
	

	for video in xmlfeed.xpath("//playlist/listitem"):
		id = video.xpath("videoid")[0].text
		title = video.xpath("headline")[0].text.decode("utf-8")
		try:
  		  summary = video.xpath("teaser")[0].text.decode("utf-8")
		except: 
		  summary = HTML.StringFromElement(video,encoding = "iso-8859-1")
  		  summary = summary[summary.find('<teaser>')+8:]
		  summary = summary[:summary.find('<')]

		try: 
		  thumbpath = video.xpath("thumb")[0].text
		except: 
		  thumbpath = ''
		
		dir.Append(Function(DirectoryItem(ParseVideoXML, title=title, summary = summary, thumb=Function(GetThumb,path = thumbpath)),title =title, summary = summary, thumbpath = thumbpath, link = (VIDEOXML_URL%id)))
    
	dir.Append(Function(DirectoryItem(ParseCategoryXML, title="Nachste Zeite"),title = title, link = link , page = page + 1))

	return dir     

def ParseVideoXML(sender, title, summary, thumbpath, link):
	dir = MediaContainer(art = R(ART), viewGroup = "List", title2 = title)
	Log(link)
	xmlfeed = HTML.ElementFromURL(link,encoding = "iso-8859-1")

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
		
		