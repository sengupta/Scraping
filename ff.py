import lxml.html
import requests
import os
sheet = []
url = 'http://www.wogma.com/genres/'
page = requests.get(url)     # Requesting the required Page
document_tree = lxml.html.fromstring(page.text)
link = document_tree.xpath('//tr[@class="odd"]/td/a/@href')  #Extracting the links to various genres
link1 = document_tree.xpath('//tr[@class="even"]/td/a/@href')   #Extracting the links to various genres
link.extend(link1)   # Merging the above extraced links
for u in link:
    iurl = 'http://wogma.com' + u
    dir = u.split('/')[2]
    path = 'reviews/' + dir
    if not os.path.exists(path):
            os.makedirs(path)   # Creating  Genre Directory
    ipage = requests.get(iurl)  #Requesting the required Genre Page
    doc_tree = lxml.html.fromstring(ipage.text)
    ilink = doc_tree.xpath('//td[@class="listing_synopsis"]/div[@class="button related_pages review "]/a/@href') # Extracting links from Genre Page
    for k in ilink:                        # Loop to run across the movies of selected genre
        add = 'http://wogma.com' + k
        print add
        title = k.split("/")[2]
        title = title.replace('-review','') + '.txt'
        revname = path + "/" +title
        if not os.path.exists(revname):
            rpage = requests.get(add)                   # Requesting the movie review page
            doc2_tree = lxml.html.fromstring(rpage.text)
            target = open (revname, 'a')
            review = doc2_tree.xpath('//div[@class="review large-first-letter"]/p/text()')   # Extracting the review
            lrevi = ' '.join(review).encode('utf-8')       # Encoding in UTF-8
            target.write(lrevi)                   # Saving the content in a file
            target.close()
            print target
        print 'done'
