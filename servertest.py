import app

#print(app.facility_id_set)
print(app.facilities)

allFac = len(app.facilities)
print("This is the total number of items in the csv file given : ",allFac)
totalData = app.db.session.query(app.Place.id_num).count()
print("This is the total number of items in the database : ", totalData)

allCon = (app.counter)
print("This is the total number of data about california in the csv file :", allCon) 
totalDataCon = app.db.session.query(app.County.id_num).count()
print("This is the total number of items in the database for the contry of california: ", totalDataCon)
