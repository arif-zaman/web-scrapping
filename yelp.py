import time
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from difflib import SequenceMatcher
from timeit import default_timer as timer
from bs4 import BeautifulSoup


def readFiles():
	print "Reading Files ...."
	print

	global cityList, searchTerms, ignore

	with open("cityList.txt", "r") as ff:
		cityList = [ line.replace("\n","").replace("\t","").strip() for line in ff.readlines()]
		print cityList

	with open("searchTerms.txt", "r") as ff:
		searchTerms = [ line.replace("\n","").replace("\t","").strip()  for line in ff.readlines()]
		print searchTerms

	# with open("ignore.txt", "r") as ff:
	# 	ignore = [ line.replace("\n","").replace("\t","").strip()  for line in ff.readlines()]
	# 	print ignore

	print
	print "File Read Successful ..."
	print


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def main():
	readFiles()
	count = 0
	for city in cityList:
		for term in searchTerms:
			startTime = timer()

			infoList, stall2Remove, stallCount = [],set([]), {}
			count = count + 1
			print ("%d - %s, %s") % (count, term, city)
			print
			
			firefox.get("https://www.yelp.com/columbus-oh-us")

			try:
				typeName = firefox.find_element_by_id("find_desc").clear()
				typeName = firefox.find_element_by_id("find_desc")
				print "Set Type : TRUE"
				typeName.send_keys(str(term))
			except Exception, e:
				print e
				print "Set Type : FALSE"

			try:
				loc = firefox.find_element_by_id("dropperText_Mast").clear()
				loc = firefox.find_element_by_id("dropperText_Mast")
				print "Set Location : TRUE"
				loc.send_keys(str(city) + Keys.RETURN)
			except Exception, e:
				print e
				print "Set Location : FALSE"

			print

			try:
				URL = firefox.find_elements(By.XPATH,'//li[@class="regular-search-result"]')
				try:
					pageNo, linkAdded, linkIgnored = 0, 0, 0
					crawl = True

					while(crawl):
						pageNo = pageNo + 1
						try:
							results = firefox.find_elements(By.XPATH,'//div[@class="search-result natural-search-result"]')
						except Exception, e:
							print e
							print " Page - %d : Get Results Failed!" % (pageNo)

						print ("%d. %s, %s - Page - %d : %d") % (count, term, city, pageNo, len(results))
						print

						try:
							for result in results:
								add, info = True, []

								blockResult = result.get_attribute('innerHTML')
								soup = BeautifulSoup(blockResult, "lxml")
								try:
									businessName = soup.find("a",class_="biz-name").get_text(" ", strip=True)
									#print businessName

									if businessName in stallCount:
										stallCount[businessName] = stallCount[businessName] + 1
										if stallCount[businessName] > limit:
											stall2Remove.add(businessName)
									else:
										stallCount[businessName] = 1
								except Exception, e:
									print e
									businessName = ""
									print "Can't Get Business Name.."

								try:
									address = soup.find("address").get_text(", ", strip=True).split(",")
									#print address
									try:
										streetAddress = address[0].strip()
										#print streetAddress
									except Exception, e:
										print e
										streetAddress = ""
										print "Can't Get Street Address"
									try:
										addressLocality = address[1].strip()
										# print addressLocality
									except Exception, e:
										print e
										addressLocality = ""
										print "Can't Get Address Locality.."
									try:
										addressRegion = address[2].strip().split(" ")[0].strip()
										# print addressRegion
									except Exception, e:
										print e
										addressRegion = ""
										print "Can't Get Address Region.."

									try:
										postalCode = address[2].strip().split(" ")[1].strip()
										# print postalCode
									except Exception, e:
										print e
										postalCode = ""
										print "Can't Get Postal Code.."
								except Exception, e:
									print e
									streetAddress = ""
									addressLocality = ""
									addressRegion = ""
									postalCode = ""
									print "Can't Get Address.."

								try:
									streetAddress2 = soup.find("span",class_="neighborhood-str-list").get_text(" ", strip=True)
									streetAddress = streetAddress + ", " + streetAddress2
									#print streetAddress2
								except Exception, e:
									print e
									print "Can't Get Street Address 2nd Part.."
									print

								try:
									phone = soup.find("span",class_="biz-phone").get_text(" ", strip=True)
									#print phone
								except Exception, e:
									print e
									phone = ""
									print "Can't Get Phone Number.."								


								#print addressLocality.strip().lower(), city.split(",")[0].strip().lower()
								if addressLocality.strip().lower() != city.split(",")[0].strip().lower():
									add = False
								# else:
								# 	for entry in ignore:
								# 		if similar(businessName, entry) >= 0.8:
								# 			print "ignore : %s" % (businessName)
								# 			add = False
								# 			break

								if add:
									linkAdded = linkAdded+1
									info.append(businessName)
									info.append(streetAddress)
									info.append(addressLocality)
									info.append(addressRegion)
									info.append(postalCode)
									info.append(phone)

									# print info
									for value in info:
										print value

									print
									if info not in infoList:
										infoList.append(info)
								else:
									linkIgnored = linkIgnored + 1
									print "Result Ignored ...."
									print

							print "Total Entry : %d" % (linkAdded)
							print
						except Exception, e:
							print e
							print "Pagination Entry Add Failed!"

						try:
							page = firefox.find_elements(By.XPATH,'//a[@class="u-decoration-none next pagination-links_anchor"]')
							if len(page)>0:
								#page[0].click()
								webLink = page[0].get_attribute('href')
								firefox.get(webLink)
								crawl = True
							else:
								crawl = False
						except Exception, e:
							print e
							print "Pagination Stopped!"
				except Exception, e:
					print e
					print "Pagination Error!"
					
			except Exception, e:
				print e
				print "No Data Available!!!!"

			print "%s, %s : Total Entry - %d" % (term, city, linkAdded)
			print "%s, %s : Total Ignored - %d" % (term, city, linkIgnored)

			wb = Workbook()
			ws = wb.active
			ws.title = term
			excelFileName = "yelp - " + term + ", " + city + ".xlsx"

			linkAdded, linkIgnored, stall2Remove = 0, 0, list(stall2Remove)
			for entry in infoList:
				if entry[0] in stall2Remove:
					linkIgnored = linkIgnored + 1
				else:
					linkAdded = linkAdded + 1
					ws.append(entry)

			print "%s, %s : Total Entry After Cleanup - %d" % (term, city, linkAdded)
			print "%s, %s : Total Ignored in Cleanup Process - %d" % (term, city, linkIgnored)

			try:
				wb.save(excelFileName)
				print "%s Successfully Saved ..." % (excelFileName)
			except Exception, e:
				print e


			endTime = timer()
			print "%s, %s Run Time : %4.2f min" % (term, city, (endTime - startTime)/(60.0))


if __name__ == '__main__':
	start = timer()
	firefox = webdriver.Firefox()
	firefox.implicitly_wait(10)

	cityList, searchTerms, ignore = [], [], []
	limit = 3
	main()
	firefox.close()
	end = timer()
	print "Complete Run Time : %4.2f min" % ((end - start)/(60.0))