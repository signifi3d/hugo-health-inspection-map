'''
UpdateChecker.py

A script to check the OHA Healthspace entries against existing 
database entries, then updates changes and marks facilities that
may have been removed from OHA's database.

10/20/2018
'''
from HealthSpaceDriver import HealthSpaceDriver
from HealthSpaceContainers import Facility
from HealthSpaceDB import HealthSpaceDB

database = HealthSpaceDB()
driver = HealthSpaceDriver()

databaseFacilities = database.getAllNameIDPairs()

for facility in databaseFacilities[1983:]:
	facilityHolder = Facility()
	facilityHolder.name = facility[0]
	facilityHolder.ID = facility[1]
	print("Loading " + facility[0])
	if not driver.loadFacilityPage(facility[1]):
		print("Facility: " + facility[0] + " ID: " + facility[1] + " possibly removed.")
		continue
	print("Grabbing facility data for ID: " + facility[1])
	driver.getCurrentPageFacilityData(facilityHolder)
	print("Grabbing current database facility entry")
	currentFacility = database.convertEntryToFacilityByID(facility[1])
	if not currentFacility.isFacilityDataEqual(facilityHolder):
		driver.getCurrentPageInspectionData(facilityHolder)
		database.updateRestaurant(facilityHolder)
