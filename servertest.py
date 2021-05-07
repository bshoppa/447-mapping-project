import app

def db_load():
    # intended file: CA-historical-data.csv (16327 lines long)
    # intended file: us-counties.csv (1280792 lines long)

    # given a csv file has a single header line and a single blank line at the end,
    # there should be 16325 entries in the database and in facilities
    # and there should be 33974 entries in the county list (not included in the test) and in the database.



    # print(app.facility_id_set)
    # print(app.facilities)

    allFac = len(app.facilities)
    print("This is the total number of items in the csv file given : ",allFac)
    totalData = app.db.session.query(app.Place.id_num).count()
    print("This is the total number of items in the database : ", totalData)

    allCon = (app.counter)
    print("This is the total number of data about california in the csv file :", allCon)
    totalDataCon = app.db.session.query(app.County.id_num).count()
    print("This is the total number of items in the database for the contry of california: ", totalDataCon)

    allCountyJsons = len(app.counties)
    return {
        'facilities' : allFac,
        'countyjsons': allCountyJsons,
        'counties' : allCon,
        'countiesdb' : totalDataCon
    }


def acquire_facility_list(date): # similar to implementation of /data. does not directly test /data, but can help to diagnose database issues.
    # (date is a mandatory field here.)
    subquery = app.Place.query.filter(app.Place.Date <= date).order_by(app.Place.Date.desc())
    query_value = app.Place.query.select_entity_from(subquery).group_by(app.Place.Facility_ID)
    return list(query_value.all())

def acquire_county_list(date):
    subquery = app.County.query.filter(app.County.Date <= date).order_by(app.County.Date.desc())
    query_value = app.County.query.select_entity_from(subquery).group_by(app.County.Name)
    return list(query_value.all())


def main():
    GREEN = '\033[92m'
    RED = '\033[91m'
    DEFORMAT = '\033[0m'

    pass_fail_dict = {}

    # ensure that database loads with correct number of entries. (too difficult to independently verify countiesdb, because it is too difficult to manually define the count of rows of counties of california. just assume that a similar number is )
    default_out = {'facilities': 16325, 'countyjsons' : 58,'counties': 33974, 'countiesdb' : 33974}
    def db_load_test():
        results = db_load()
        if results['counties'] != results['countiesdb']:
            raise Exception('database failure - ' + str(results['counties']) + ' in counties, ' + str(results['countiesdb']) + ' in counties database.')
        for key in default_out:
            if results[key] != default_out[key]:
                raise Exception('mismatch ' + key)

    # a list of dates that we believe should contain different objects.
    dates = [
        '2021-05-01',
        '2021-03-30',
        '2021-03-01',
        '2021-01-01',
        '2020-05-01'
    ]

    # ensure difference between lists. basic test only.
    def db_difference_test():
        placeLists = [
            acquire_facility_list(date) for date in dates
        ]
        countyLists = [
            acquire_county_list(date) for date in dates
        ]

        for i in range(len(placeLists)):
            for j in range(i):
                if placeLists[i] == placeLists[j]:
                    raise Exception('identical place lists on dates ' + dates[i] + ' and ' + dates[j])
        for i in range(len(countyLists)):
            for j in range(i):
                if countyLists[i] == countyLists[j]:
                    raise Exception('identical county lists on dates ' + dates[i] + ' and ' + dates[j])

    # ensure that the same result comes from the database when the same request is made twice in a row.
    def db_difference_test_contrast():
        placeLists = [
            acquire_facility_list(date) for date in dates
        ]
        countyLists = [
            acquire_county_list(date) for date in dates
        ]
        for i in range(len(placeLists)):
            if placeLists[i] != acquire_facility_list(dates[i]):
                raise Exception('differing facility lists on date ' + dates[i])
        for i in range(len(countyLists)):
            if countyLists[i] != acquire_county_list(dates[i]):
                raise Exception('differing county lists on date ' + dates[i])

    # ensure that database query results are valid, contains nonzero entries, and contain nonzero case data for intended dates.
    def db_content_return_test():
        placeLists = [
            acquire_facility_list(date) for date in dates
        ]
        countyLists = [
            acquire_county_list(date) for date in dates
        ]
        for i in range(len(placeLists)):
            print("A list of ", len(placeLists[i]), " facilities loaded on date " + dates[i])
            if len(placeLists[i]) < 15:
                raise Exception('too few facilities on date ' + dates[i])

        for i in range(len(countyLists)):
            if len(countyLists[i]) < default_out['countyjsons']:
                county_names = [county.Name for county in countyLists[i]]
                # attempt to find out if any counties are missing.
                for county_name in app.counties:
                    if county_name not in county_names:
                        print(county_name, "not in countyLists[i]")

                print(len(countyLists[i]), len(app.counties))

                raise Exception('county missing on date ' + dates[i] + ' (# of counties:)' + str(county_names))

    # make sure entry names, ids, case numbers, locations, etc. are valid.
    # % of valid locations returned. having a listed location is often optional for facilities.
    def db_formatting_test():
        placeLists = [
            acquire_facility_list(date) for date in dates
        ]
        countyLists = [
            acquire_county_list(date) for date in dates
        ]

        locations_dict = {}
        cases_dict = {}

        for i in range(len(placeLists)):
            for place in placeLists[i]:
                Cases = place.Cases
                Date = place.Date
                if Date > dates[i]:
                    raise Exception('DATE FROM THE FUTURE : ROW = ' + str(place.id_num) + ' facility id = ' + str(place.Facility_ID))
                try:
                    if int(Cases) < 0:
                        raise Exception('NEGATIVE CASE : ROW = ' + str(place.id_num) + ' facility id = ' + str(place.Facility_ID))
                    cases_dict[place.Facility_ID] = Cases
                except ValueError as err:
                    pass
                try:
                    locations_dict[place.Facility_ID] = [float(place.Latitude), float(place.Longitude)]
                except ValueError as err:
                    pass

        locations_valid = len(locations_dict)
        return str(locations_valid) + ' / ' + str(len(locations_dict)) + ' valid locations, ' + str(len(cases_dict)) + ' / ' + str(len(locations_dict)) + ' facilities have case values.'


    tests = [
        db_load_test,
        db_difference_test,
        db_difference_test_contrast,
        db_content_return_test,
        db_formatting_test
    ]

    for test in tests:
        try:
            result = test()
        except Exception as err:
            pass_fail_dict[test.__name__] = RED + str(err) + DEFORMAT
            print("Test failed with exception")
            print(RED + str(err) + DEFORMAT)
        else:
            pass_fail_dict[test.__name__] = GREEN + 'passed ' + str(result) + DEFORMAT
            print(GREEN + "Test passed" + DEFORMAT)

    #print test summary
    print("\n\nTEST SUMMARY")
    for test in pass_fail_dict:
        print(test, "result:")
        print(pass_fail_dict[test])

    print(sum([1 if 'passed' in pass_fail_dict[i] else 0 for i in pass_fail_dict]), "/", len(pass_fail_dict), "tests passed.")

main()
