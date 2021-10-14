from database_services.RDBService import RDBService


def t1():

    res = RDBService.get_by_prefix(
        "imdbfixed", "names_basic", "primary_name", "Tom H"
    )
    print("t1 resule = ", res)


def t2():

    # res = RDBService.find_by_template(
    #     "imdbfixed", "names_basic_recent", {"primaryName": "Tom Hanks"}, None
    # )
    res = RDBService.find_by_template(
        "e6156", "users", None, None
    )
    print("t2 resuls = ", res)


def t3():

    res = RDBService.create(
        "e6156", "users",
            {
                "first_name": "Tom",
                "last_name": "Hanks",
                "uni": "th2713",
                "email": "th2713@columbia.edu",
                "role": "student"
            })
    print("t3: res = ", res)

# t2()
t3()


