"""
Relevant MySQL database handling class.

"""

import pymysql
import config
from HealthSpaceContainers import Facility
from HealthSpaceContainers import Inspection

class HealthSpaceDB:
	def __init__(self):
		self.connection = pymysql.connect(host=config.DBSERVER, user=config.DBUSER, password=config.DBPASS, db=config.DBNAME)
		self.cursor = self.connection.cursor()

	def executeInsertOrUpdateQuery(self, queryToExecute):
		self.cursor.execute(queryToExecute[0], queryToExecute[1])
		self.connection.commit()

	def cleanUp(self):
		self.cursor.close()
		self.connection.close()

	def getAllNameIDPairs(self):
		sqlRequest = 'SELECT rest_name, rest_id FROM restaurants'
		self.cursor.execute(sqlRequest)
		nameIDPairs = self.cursor.fetchall()
		return nameIDPairs

	def getNonGeocodedEntries(self):
		sqlRequest = "SELECT rest_id, street_address, city_section, street_name, city, zip_code FROM restaurants WHERE latitude IS NULL"
		self.cursor.execute(sqlRequest)
		return self.cursor.fetchall()
		
	def updateRestaurant(self, facilityData):
		self.executeInsertOrUpdateQuery(self.convertFacilityToUpdateQuery(facilityData))

		for inspectionInsertQuery in self.convertInspectionsToInsertQueryList(facilityData):
			self.executeInsertOrUpdateQuery(inspectionInsertQuery)
			

	def convertFacilityToUpdateQuery(self, facilityToConvert):
		'''
		Takes in a Facility object and builds a string to submit
		to the database to update a Facility.
		Returns the built string as well as a tuple of arguments.
		'''
		updateString = 'UPDATE restaurants SET '
		updateStringData = ()
		if facilityToConvert.ID == '':
			print("ID number required to update entry.")
			return ''
		if facilityToConvert.name != '':
			updateString = updateString + 'rest_name = %s, '
			updateStringData += (facilityToConvert.name,)
		if facilityToConvert.address != None:
			if facilityToConvert.address.addressNumber != '':
				updateString += 'street_address = %s, '
				updateStringData += (facilityToConvert.address.addressNumber,)
			if facilityToConvert.address.citySection != '':
				updateString += 'city_section = %s, '
				updateStringData += (facilityToConvert.address.citySection,)
			updateString += 'street_name = %s, ' \
					+ 'city = %s, ' \
					+ 'zip_code = %s, '
			updateStringData += (facilityToConvert.address.streetName, facilityToConvert.address.city, facilityToConvert.address.zip)
		if facilityToConvert.lastInspection != '':
			updateString = updateString + 'last_inspection = %s, '
			updateStringData += (facilityToConvert.lastInspection,)
		if facilityToConvert.facilityType != '':
			updateString = updateString + 'rest_type = %s, '
			updateStringData += (facilityToConvert.facilityType,)
		if facilityToConvert.status != '':
			updateString = updateString + 'rest_status = %s, '
			updateStringData += (facilityToConvert.status,)
		if facilityToConvert.phone != '':
			updateString = updateString + 'phone_num = %s'
			updateStringData += (facilityToConvert.phone,)
		if updateString[len(updateString)-2:len(updateString)]==', ':
			updateString = updateString[0:len(updateString)-2]
		updateString = updateString + " WHERE rest_id = %s "
		updateStringData += (facilityToConvert.ID,)

		return updateString, updateStringData

	def convertFacilityToInsertQuery(self, facilityToConvert):
		insertString = 'INSERT IGNORE INTO restaurants (rest_id, rest_name '
		formatSpecifierString = 'VALUES (%s, %s'
		formatSpecifierTuple = (facilityToConvert.ID, facilityToConvert.name)
		if facilityToConvert.address.addressNumber != '':
			insertString += ', street_address'
			formatSpecifierString += ', %s'
			formatSpecifierTuple += (facilityToConvert.address.addressNumber,)
		if facilityToConvert.address.citySection != '':
			insertString += ', city_section'
			formatSpecifierString += ', %s'
			formatSpecifierTuple += (facilityToConvert.address.citySection,)
		insertString += ', street_name, city, zip_code'
		formatSpecifierString += ', %s, %s, %s'
		formatSpecifierTuple += (facilityToConvert.address.streetName, facilityToConvert.address.city, facilityToConvert.address.zip)
		if facilityToConvert.lastInspection != '':
			insertString += ', last_inspection'
			formatSpecifierString += ', %s'
			formatSpecifierTuple += (facilityToConvert.lastInspection,)
		if facilityToConvert.facilityType != '':
			insertString += ', rest_type'
			formatSpecifierString += ', %s'
			formatSpecifierTuple += (facilityToConvert.facilityType,)
		if facilityToConvert.status != '':
			insertString += ', rest_status'
			formatSpecifierString += ', %s'
			formatSpecifierTuple += (facilityToConvert.status,)
		if facilityToConvert.phone != '':
			insertString += ', phone_num'
			formatSpecifierString += ', %s'
			formatSpecifierTuple += (facilityToConvert.phone,)
		return insertString + ') ' + formatSpecifierString + ')', formatSpecifierTuple	

	def convertInspectionsToInsertQueryList(self, facilityData):
		insertStringList = ()
		insertString = "INSERT IGNORE INTO inspections (rest_id, insp_date, score, insp_reason) VALUES (%s, %s, %s, %s)"
		for inspection in facilityData.inspections:
			insertDataTuple = ( facilityData.ID, inspection.inspectionDate, inspection.inspectionScore, inspection.inspectionReason )
			insertStringList += ((insertString, insertDataTuple),)
		return insertStringList 

	def facilityEntryExists(self, facilityID):
		sqlRequest = 'SELECT rest_name FROM restaurants WHERE rest_id = %s'
		self.cursor.execute(sqlRequest, (facilityID,))
		if len(self.cursor.fetchall()) > 0:
			return True
		return False	

	def checkFacilityChanges(self, facilityDataToCheck):
		if not self.facilityEntryExists(facilityDataToCheck.ID):
			print("Inserting New Facility")
			self.insertNewFacility(facilityDataToCheck)
		elif self.diffFacilityEntry(facilityDataToCheck):
			self.updateRestaurant(facilityDataToCheck)
			print("Updating changes.")
		else:
			print("No Changes.")
	
	def insertNewFacility(self, facilityDataToAdd):
		self.executeInsertOrUpdateQuery(self.convertFacilityToInsertQuery(facilityDataToAdd))
		
		for inspectionQuery in self.convertInspectionsToInsertQueryList(facilityDataToAdd):
			self.executeInsertOrUpdateQuery(inspectionQuery)

	def diffFacilityEntry(self, facilityDataToDiff):
		currentFacilityData = self.convertEntryToFacilityByID(facilityDataToDiff.ID)
		return not currentFacilityData.isEqual(facilityDataToDiff)
		
	
	def convertEntryToFacilityByID(self, facilityID):
		facilityDataHolder = Facility()
		sqlRequest = 'SELECT rest_name, street_address, city_section, street_name, city, zip_code, last_inspection, rest_type, rest_status, phone_num FROM restaurants WHERE rest_id=%s'
		self.cursor.execute(sqlRequest, (facilityID,))
		facilityDataList = self.cursor.fetchone()
		facilityDataHolder.ID = facilityID
		facilityDataHolder.name = facilityDataList[0]
		facilityDataHolder.address.addressNumber = str(facilityDataList[1]) if facilityDataList[1]!=None else ''
		facilityDataHolder.address.citySection = facilityDataList[2] if facilityDataList[2]!=None else ''
		facilityDataHolder.address.streetName = facilityDataList[3]
		facilityDataHolder.address.city = facilityDataList[4]
		facilityDataHolder.address.zip = facilityDataList[5]
		facilityDataHolder.lastInspection = facilityDataList[6]
		facilityDataHolder.facilityType = facilityDataList[7]
		facilityDataHolder.status = facilityDataList[8]
		facilityDataHolder.phone = facilityDataList[9]
		
		sqlRequest = 'SELECT insp_date, score, insp_reason FROM inspections WHERE rest_id=%s'
		self.cursor.execute(sqlRequest, (facilityID,))
		facilityDataList = self.cursor.fetchall()
		
		for inspection in facilityDataList:
			inspectionDataHolder = Inspection()
			inspectionDataHolder.inspectionDate = inspection[0]
			inspectionDataHolder.inspectionScore = str(inspection[1])
			inspectionDataHolder.inspectionReason = inspection[2]
			facilityDataHolder.addInspection(inspectionDataHolder)

		return facilityDataHolder

	def convertDatabaseToOutputFile(self, converter):
		#Converter must be a proper converter object type
		queryString = "SELECT r.rest_name, r.street_address, r.city_section, r.street_name, r.city, r.zip_code, r.rest_type, r.rest_status, r.last_inspection, (SELECT ROUND(AVG(score)) FROM inspections WHERE score > 0 AND rest_id = r.rest_id GROUP BY rest_id), i.score, r.longitude, r.latitude, r.rest_id FROM restaurants r JOIN inspections i ON r.rest_id=i.rest_id AND r.last_inspection=i.insp_date WHERE r.longitude IS NOT NULL"
		self.cursor.execute(queryString)
		queryResults = self.cursor.fetchall()
		converter.convert(queryResults)
