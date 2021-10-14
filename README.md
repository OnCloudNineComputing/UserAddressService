# e6156-UserAddressMicroservice

* /users
  * GET, POST
* /users/\<userID\>
  * GET, PUT, DELETE
* /users/\<userID\>/addresses
  * GET, POST, PUT, DELETE
* /addresses
  * GET, POST
* /addresses/\<addressID\>
  * GET, PUT, DELETE
* /addresses/\<addressID\>/users
  * GET, PUT, DELETE

## Users
{  
  "id": 1,  
  "first_name": "Tom",  
  "last_name": "Hanks",  
  "uni": "th1234",   
  "email": "th1234@columbia.edu",   
  "role": "TA",    
  "address_id": NULL  
}

## Addresses
{  
  "id": 1,  
  "room": "451",  
  "building": "CS",  
}
