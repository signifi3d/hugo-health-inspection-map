'''
Goes through every entry on the OHA Healthspace web site and
checks for those that aren't currently in the mapper database.
'''

from HealthSpaceDriver import HealthSpaceDriver
from HealthSpaceContainers import Facility
from HealthSpaceDB import HealthSpaceDB
from Converter import GeoJSONConverter
from geopy.geocoders import Here
from geopy.exc import GeocoderTimedOut
from geopy.exc import GeocoderServiceError
import config

geocoder = Here(config.GEOCODER_APP_ID, config.GEOCODER_APP_CODE)
database = HealthSpaceDB()
driver = HealthSpaceDriver()
facilityHolder = Facility()

def geocode_get(string_in):
	location = None
	try: 
		location = geocoder.geocode(string_in)
	except GeocoderTimedOut:
		return geocode_get(string_in)
	except GeocoderServiceError:
		print(string_in + "Service Error")
		return None
	return location

while driver.getNextNameAndID(facilityHolder):
	if not database.facilityEntryExists(facilityHolder.ID):
		print ("Adding new facility: " + facilityHolder.name + " " + facilityHolder.ID)
		facilityHolder = driver.getFacilityData(facilityHolder.ID)
		database.insertNewFacility(facilityHolder)		

unpaired_addresses = database.getNonGeocodedEntries()

for address in unpaired_addresses:
	address_string = ''
	for i in range(1,6,1):
		if address[i] is not None:
			address_string += str(address[i]) + ' '
	location = geocode_get(address_string)
	if location is not None:
		updateString = "UPDATE restaurants SET latitude="+str(location.latitude)+", longitude="+str(location.longitude)+" WHERE rest_id='"+address[0]+"'"
		print(updateString)
		database.cursor.execute(updateString)
		database.connection.commit()

database.convertDatabaseToOutputFile(GeoJSONConverter())

database.cleanUp()
