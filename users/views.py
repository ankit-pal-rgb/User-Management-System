import json
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from bson import ObjectId
from bson.json_util import dumps
from .db_connection import users_collection
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage



@csrf_exempt
def convert_id(user):
    user["id"] = str(user['_id'])
    del user['_id']
    return user

@csrf_exempt
def get_user_by_id(request, id):
    if request.method!='GET':
        return JsonResponse({'error' : 'Invalid http method!'}, status=405)
    
    try:
        user = users_collection.find_one({'_id':ObjectId(id)})
        if not user:
            return JsonResponse({'error' : 'User Not Found!'}, status=404)
        else:
            return JsonResponse(convert_id(user), status=200)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=400)    
     
@csrf_exempt    
def get_all_users(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid HTTP method!'}, status=405)

    # Get query parameters
    username = request.GET.get("username")
    email = request.GET.get("email")
    age = request.GET.get("age")

    query = {}

    if username:
        query["username"] = {"$regex": username, "$options": "i"}  # case-insensitive
    if email:
        query["email"] = {"$regex": email, "$options": "i"}  # case-insensitive
    if age:
        try:
            query["age"] = int(age)
        except ValueError:
            return JsonResponse({"error": "Age must be an integer."}, status=400)

    # Fetch filtered users
    users = list(users_collection.find(query))
    data = [convert_id(user) for user in users]

    return JsonResponse(data, safe=False, status=200)



@csrf_exempt
def update_user(request, id):
    if request.method!='PUT':
        return JsonResponse({'error':'Invalid http method'}, status=405)
    try:
        data = json.loads(request.body)
        result = users_collection.update_one({'_id':ObjectId(id)},{'$set':data})
        if result.matched_count==0:
            return JsonResponse({'error':'No user found'}, status=404)
        return JsonResponse({'message':'User Updated'}, status=200)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=400)


@csrf_exempt
def delete_user(request, id):
    if request.method!='DELETE':
        return JsonResponse({'error':'Invalid http method'}, status=405)
    try:
        result = users_collection.delete_one({'_id':ObjectId(id)})
        if result.deleted_count==0:
            return JsonResponse({'error':'No user found'}, status=404)
        return JsonResponse({'message':'User Deleted'}, status=200)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=400)
    

@csrf_exempt
def add_new_user(request):
    if request.method!='POST':
        return JsonResponse({'error':"Invalid http method"}, status=405)
    
    try:
        data = json.loads(request.body)
        result = users_collection.insert_one(data)
        data['_id'] = str(result.inserted_id)
        return JsonResponse({'message':'User Added', 'id':str(result.inserted_id)}, status=201)
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=400)

@csrf_exempt
def render_register_form(request):
    return render(request, "users/registration_form.html")

@csrf_exempt
def register_user_with_picture(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')  # 🔒 You should hash this
        profile_picture = request.FILES.get('profile_picture')

        if not username or not email or not password:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        profile_picture_path = None
        if profile_picture:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_pics'))
            filename = fs.save(profile_picture.name, profile_picture)
            profile_picture_path = f"profile_pics/{filename}"

        # Insert user into MongoDB
        user = {
            "username": username,
            "email": email,
            "password": password,  # 🔒 Hash in production
            "profile_picture": profile_picture_path
        }

        result = users_collection.insert_one(user)

        return JsonResponse({
            'message': 'User registered successfully',
            'id': str(result.inserted_id),
            'profile_picture': profile_picture_path
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

        
    


