"""
HealthSpaceContainers includes all of the data structures for holding restaurant
and inspection data.
"""

import string

class Facility:
	def __init__(self):
        	self.ID=''
        	self.name=''
        	self.address=Address()
        	self.lastInspection=''
        	self.facilityType=''
        	self.status=''
        	self.phone=''
        	self.inspections=[]
        
	def setAddress(self, addressString):
        	self.address.setAddress(addressString)
        
	def addInspection(self, inspectionToAdd):
		self.inspections.append(inspectionToAdd)
	
	def isEqual(self, facilityToEqual):
		if self.ID != facilityToEqual.ID:
			print("Different ID")
			return False
		elif self.name != facilityToEqual.name:
			print("Different Name")
			return False
		elif not self.address.isEqual(facilityToEqual.address):
			print("Different address")
			return False
		elif self.lastInspection != facilityToEqual.lastInspection and not ((self.lastInspection is None or self.lastInspection == '') and (facilityToEqual.lastInspection is None or facilityToEqual.lastInspection == '')):
			print("Different last inspection")
			return False
		elif self.facilityType != facilityToEqual.facilityType:
			print("Different facility type.")
			return False
		elif self.status != facilityToEqual.status:
			print("Different status")
			return False
		elif self.phone != facilityToEqual.phone and not ((self.phone is None or self.phone == '') and (facilityToEqual.phone is None or facilityToEqual.phone == '')):
			print("Different phone number.")
			return False
		elif len(self.inspections) != len(facilityToEqual.inspections):
			print("Different # of inspections.")
			return False
		for i in range(0, len(self.inspections),1):
			for j in range(0, len(facilityToEqual.inspections),1):
				if self.inspections[i].isEqual(facilityToEqual.inspections[j]):
					break
				elif j == len(facilityToEqual.inspections)-1:
					print("Different inspection data.")
		print("Facility data are equal.")
		return True

	def isFacilityDataEqual(self, facilityToEqual):
		if self.ID != facilityToEqual.ID:
			print("Different ID")
			return False
		elif self.name != facilityToEqual.name:
			print("Different Name")
			return False
		elif not self.address.isEqual(facilityToEqual.address):
			print("Different address")
			return False
		elif self.lastInspection != facilityToEqual.lastInspection and not ((self.lastInspection is None or self.lastInspection == '') and (facilityToEqual.lastInspection is None or facilityToEqual.lastInspection == '')):
			print("Different last inspection")
			return False
		elif self.facilityType != facilityToEqual.facilityType:
			print("Different facility type.")
			return False
		elif self.status != facilityToEqual.status:
			print("Different status")
			return False
		elif self.phone != facilityToEqual.phone and not ((self.phone is None or self.phone == '') and (facilityToEqual.phone is None or facilityToEqual.phone == '')):
			print("Different phone number.")
			return False
		print("Facility data are equal.")
		return True


class Inspection:
	def __init__(self):
		self.inspectionDate=''
		self.inspectionReason=''
		self.inspectionScore=''
	
	def isEqual(self, inspectionToEqual):
		if self.inspectionDate != inspectionToEqual.inspectionDate:
		#	print("Inspection date 1: " + self.inspectionDate + " Date 2: " + inspectionToEqual.inspectionDate)
			return False
		elif self.inspectionReason != inspectionToEqual.inspectionReason:
		#	print("Reason 1: " + self.inspectionReason + " Reason 2: " + inspectionToEqual.inspectionReason)
			return False
		elif self.inspectionScore != inspectionToEqual.inspectionScore:
		#	print("Score 1: " + self.inspectionScore + " Score 2: " + inspectionToEqual.inspectionScore)
			return False
		return True
	
	def __str__(self):
		return self.inspectionDate + " " + self.inspectionReason + " " + self.inspectionScore;	
        
class Address:
	'''
	Address is a data type that holds address data, specifically tuned for 
	Portland Oregon's address structure of accounting for the section of the 
	city. Address holds data by adress number, city section, street name, city,
	and zip code. State is assumed to be Oregon. There may be no address number
	in which case the street name will represent an intersection of two streets.
	'''
	citySections=('N','E','W','NW','NE','SW','SE')
	def __init__(self, addressToConvert=''):
		self.addressNumber=''
		self.citySection=''
		self.streetName=''
		self.city=''
		self.zip=''
		self.state='OR'
		if addressToConvert != '':
			self.setAddress(addressToConvert)
        
	def setAddress(self, addressToConvert):
		'''
		Takes the input string and fills in all of the address variables using
		the given string. First strings are split into comma separated sections.
		The address is checked to see if it begins with an address number, then
		a city section, if neither are present then it just records the string up
		to the first comma in the address string. Note: Only works with addresses
		that are in the format [street address], [city], [state] [zip], both 
		commas must be present. 
		TODO account for situations where the address is formatted [street address],
		[city], [state], [zip]
		'''
		addressComponents = addressToConvert.split(',')
		streetAddressComponents = addressComponents[0].split()
		stateZipComponents = addressComponents[2].split()
		self.city = addressComponents[1]
		self.zip= stateZipComponents[1]
		#Check for address validity by zipcode length and that they're digits
		if len(stateZipComponents[1]) != 5 or stateZipComponents[1][0] not in string.digits:
    			print("Invalid zip code.")
		#Address numbers and city sections might not be present, seperate checks
		#are made for both, address number first, then city section, then the 
		#rest of the street address is recorded. It is assumed that city section
		#never comes first.
		if addressComponents[0][0] in string.digits:
            		#Since the first part of the address is a digit it can be assumed to be the address number
            		self.addressNumber=streetAddressComponents[0]
            		#Remove the address number from the address component list
            		streetAddressComponents = streetAddressComponents[1:]
		if streetAddressComponents[0] in self.citySections:
		#check to see if the next component of the street address is a city section
			self.citySection=streetAddressComponents[0]
            		#Remove the city section component from the address component list
			streetAddressComponents = streetAddressComponents[1:]
		#Add remaining components to street name variable
		for i in range(0,len(streetAddressComponents),1):
			self.streetName=self.streetName+" "+streetAddressComponents[i]
	def isEqual(self, addressToEqual):
		if self.addressNumber != addressToEqual.addressNumber:
			return False
		elif self.citySection != addressToEqual.citySection:
			return False		
		elif self.streetName != addressToEqual.streetName:
			return False
		elif self.city != addressToEqual.city:
			return False
		elif self.zip != addressToEqual.zip:
			return False
		return True
        
	def convertAddress(self, addressToConvert):
		return Address(addressToConvert)
        
	def __str__(self):
		if self.addressNumber != '':
			return self.addressNumber + " " + self.citySection + " " + self.streetName + "," + self.city + ", " + self.state + " " + self.zip
		return self.citySection + " " + self.streetName + "," + self.city + ", " + self.state + " " + self.zip
