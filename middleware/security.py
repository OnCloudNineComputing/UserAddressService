


paths = ['/', '/login', '/users', 'addresses']

def check_security_path(request, logged_in):
    path = request.path
    res = False
    if path in paths:
        print ("The path is not secure, allowing request to proceed")
        res = True
    else:
        if logged_in:
            print("The path is secure, and the user is logged in")
            res = True
        else:
            print("The path is secure, and the user is NOT logged in")

    return res
