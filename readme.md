# Django + MongoDB User Management API

## Run Locally with Docker

```bash
docker-compose build
docker-compose up
````

## For homepage
````bash
http://127.0.0.1:8000/
````

## Get User By Id
````bash
http://127.0.0.1:8000/user-management-system/get-user/{id}
````

## Get All Users
````bash
http://127.0.0.1:8000/user-management-system/get-users/
````

## Update User
````bash
http://127.0.0.1:8000/user-management-system/update-user/{id}
````

## To Delete a User
````bash
http://127.0.0.1:8000/user-management-system/delete-user/{id}
````

## To Add New User
````bash
http://127.0.0.1:8000/user-management-system/user-add/
````

## For search filter
````bash
http://127.0.0.1:8000/user-management-system/get-users?email=gmail

## For Pagination
````bash
http://127.0.0.1:8000/user-management-system/get-users?username=ankit&page=1&limit=2

## Invite via email
#### Methost=POST
````bash
http://127.0.0.1:8000/user-management-system/sent-invite/
````
### Example body
````bash
{
  "email": "someone@example.com"
}
````

## Soft delete
````bash
http://127.0.0.1:8000/user-management-system/soft-delete/{id}
````

## Restore user
````bash
http://127.0.0.1:8000/user-management-system/restore-user/{id}