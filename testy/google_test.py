import googleapi

results = googleapi.standard_search.search("albert einstein")
print("%s - %s" % (len(results), results[0].description))
