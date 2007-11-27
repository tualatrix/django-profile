from profile.models import Continent, Country
import sys

if len(sys.argv) > 1 and sys.argv[0] == "manage.py" and sys.argv[1] == "runserver":
    # Import the initial data in the Country and Continent database
    if len(Continent.objects.all()) == 0:
        print "Importing  continents..."
        Continent().importdata()
    if len(Country.objects.all()) == 0:
        print "Importing  countries..."
        Country().importdata()
