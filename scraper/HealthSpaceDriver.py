"""
This is a selenium web driver that uses a headless PhantomJS driver to traverse
the healthspace web site for Multnomah county in Oregon.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import re
from HealthSpaceContainers import Facility
from HealthSpaceContainers import Inspection


class HealthSpaceDriver:
	webAddr='https://healthspace.com/Clients/Oregon/Multnomah/Web.nsf/module_facilities.xsp?module=Food'
	facilityPagePrefix='https://healthspace.com/Clients/Oregon/Multnomah/Web.nsf/formFacility.xsp?id='
	def __init__(self, initialOffset=0):
		print("Establishing driver")
		self.hsDriver=webdriver.PhantomJS()
		print("Connecting to page")
		self.hsDriver.get(self.webAddr)
		self.facilityCount=0
		self.pageOffset=initialOffset
		self.loadErrorCount=0
		
	def isNotLastPage(self):
		return EC.element_to_be_clickable((By.ID,"view:_id1:_id247:pager6__Next__lnk"))
	
	def goBackToPage(self, currOffset=50):
		self.hsDriver.get(self.webAddr)
		pageOffset=50
		print("Going back to page " + str(self.pageOffset/50))
		while pageOffset <= currOffset:
			try:
				self.hsDriver.find_element_by_id("view:_id1:_id247:pager6__Next__lnk").click()
			except NoSuchElementException:
				print("\nCouldn't load page. Next button not found. restarting..")
				print(self.facilityCount)
				print(self.pageOffset)
				pageOffset=50
				self.hsDriver.get(self.webAddr)
				continue
			try:
				WebDriverWait(self.hsDriver,20).until(EC.presence_of_element_located((By.ID, "view:_id1:_id247:repeatFacilities:"+str(pageOffset)+":facilityNameLink2")))
			except TimeoutException:
				print("\nCouldn't load page, list item didn't load. restarting...")
				print(self.facilityCount)
				print(self.pageOffset)
				pageOffset=50
				self.hsDriver.get(self.webAddr)
				continue
			pageOffset+=50
			print('.', end='')
		print('')
			
	def incrementFacilityCount(self):
		self.facilityCount+=1
		if self.facilityCount==50:
			self.pageOffset+=50
			self.facilityCount=0
			if self.isNotLastPage():
				print("Going to next page, " + str(self.pageOffset/50))
				self.hsDriver.find_element_by_id("view:_id1:_id247:pager6__Next__lnk").click()
				try:
					WebDriverWait(self.hsDriver,10).until(EC.presence_of_element_located((By.ID, "view:_id1:_id247:repeatFacilities:"+str(self.pageOffset)+":facilityNameLink2")))
				except TimeoutException:
					self.goBackToPage(self.pageOffset)	
			else:
				print("Last page reached.")

	
	def getNextNameAndID(self, nextFacility):
		self.goBackToPage(self.pageOffset)
		try:
			restNameElement = self.hsDriver.find_element_by_id("view:_id1:_id247:repeatFacilities:"+str(self.pageOffset+self.facilityCount)+":facilityNameLink2")
		except NoSuchElementException:
			print("Next facility not found.")
			return False
		nextFacility.name = restNameElement.text
		print("Loading: " + nextFacility.name)
		restNameElement.click()
		try:
			nextFacility.ID = re.search("([A-Z0-9]{32})",self.hsDriver.current_url).group(1)
		except AttributeError:
			self.loadErrorCount += 1
			if self.loadErrorCount >= 10:
				print ("Error loading page for: " + nextFacility.name)
				self.loadErrorCount = 0
				return False
			else :
				self.getNextNameAndID(nextFacility)
		self.hsDriver.back()
		self.incrementFacilityCount()
		self.loadErrorCount = 0
		return True
	
	def getFacilityData(self, facilityID):
		'''
		Navigates to a food facility page on the HealthSpace web site based on
		a provided facility ID number. Grabs the data about the facility and its
		inspections from the page and returns it in a Facility object.
		'''
		#Create temporary variable to hold all of the facility data
		facilityHolder=Facility()
		facilityHolder.ID=facilityID

		self.loadFacilityPage(facilityID)
		print("Grabbing restaurant data for facility # " + facilityID)
		self.getCurrentPageFacilityData(facilityHolder)
		print("Grabbing inspection data for facility # " + facilityID)
		self.getCurrentPageInspectionData(facilityHolder)
		return facilityHolder
	
	def getCurrentPageFacilityData(self, facilityData):
		'''
		Grabs the facility data for the current page the driver is on. Takes in a Facility object to load up with data. 
		'''
		facilityData.name=self.hsDriver.find_element_by_id("view:_id1:_id200:nameCF1").text
		facilityData.setAddress(self.hsDriver.find_element_by_id("view:_id1:_id200:facilityAddressCF1").text)
		facilityData.lastInspection=self.hsDriver.find_element_by_id("view:_id1:_id200:lastInspectionCF1").text
		facilityData.facilityType=self.hsDriver.find_element_by_id("view:_id1:_id200:subTypeCF1").text
		facilityData.status=self.hsDriver.find_element_by_id("view:_id1:_id200:statusCF1").text
		facilityData.phone=self.hsDriver.find_element_by_id("view:_id1:_id200:phoneCF1").text
			
	def getCurrentPageInspectionData(self, facilityData):
		'''
		Grabs the inspection data for the current page the driver is on. Takes in a Facility object to load with data.
		'''
		#The number of inspections will always be unknown, but the elements that
		#contain the link to the inspection have a count from 0 so we loop until
		#there isn't an element with that count number.
		inspectionCount=0
		while True:
			print("Checking for inspection " + str(inspectionCount+1))
			#create variable to temporarily hold inspection data
			inspectionHolder=Inspection()
			#Try to click on the next inspection link
			try:
				self.hsDriver.find_element_by_id("view:_id1:_id200:_id253:repeatInspections:"+str(inspectionCount)+ ":inspectionTestCF1").click()
			#If no such element then all inspections have been grabbed and loop can break
			except NoSuchElementException:
				#Sometimes the inspection list doesn't start at 0, give it another try at 1
				if inspectionCount==0:
					inspectionCount+=1
					continue
				else:
					break
			#reload the page and restart the current loop if there's a problem loading the inspection page
			try:
				WebDriverWait(self.hsDriver,20).until(EC.presence_of_element_located((By.ID, "view:_id1:_id200:_id224:facilityLink1")))
			except TimeoutException:
				print("Problems loading inspection page, retrying.")
				self.loadFacilityPage(facilityData.ID)
				continue
			#Grab and store all of the data from the page
			inspectionHolder.inspectionDate=self.hsDriver.find_element_by_id("view:_id1:_id200:_id224:inspectionDateCF1").text
			inspectionHolder.inspectionScore=self.hsDriver.find_element_by_id("view:_id1:_id200:_id224:showScoreCF11").text
			inspectionHolder.inspectionReason=self.hsDriver.find_element_by_id("view:_id1:_id200:_id224:inspTypeCF1").text
			#Add inspection data to facility data, increment the count, reload the facility page
			facilityData.addInspection(inspectionHolder)
			inspectionCount+=1
			self.loadFacilityPage(facilityData.ID)
	
	def loadFacilityPage(self, facilityID):
		'''
		In several situations it is necessary to load up a particular facility 
		page based on ID number. This function merely containerizes the process.
		'''
		try:
			self.hsDriver.get(self.facilityPagePrefix + facilityID)
			WebDriverWait(self.hsDriver,20).until(EC.presence_of_element_located((By.ID, "view:_id1:_id200:nameCF1")))
		except TimeoutException:
			if self.loadErrorCount < 10:
				print("Couldn't load page. Retrying.")
				self.loadErrorCount+=1
				self.loadFacilityPage(facilityID)
			else :
				print("Page is down or doesn't exist.")
				self.loadErrorCount=0
				return False
		self.loadErrorCount=0
		return True
		
