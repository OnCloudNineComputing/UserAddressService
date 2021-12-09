from database_services.RDBService import RDBService


def test_2():
    res = RDBService.update_by_template(
        "e6156", "addresses", {"Building": "CSE"}, {"id": "1"}
    )
    print("Test 2 result = ", res)


test_2()
