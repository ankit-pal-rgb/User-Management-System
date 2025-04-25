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
import uuid
from django.core.mail import send_mail
from django.conf import settings



@csrf_exempt
def convert_id(user):
    user["id"] = str(user['_id'])
    user["is_deleted"] = user.get("is_deleted", False)
    del user['_id']
    return user


@csrf_exempt
def get_user_by_id(request, id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid http method!'}, status=405)

    try:
        user = users_collection.find_one({'_id': ObjectId(id), 'is_deleted': {'$ne': True}})
        if not user:
            return JsonResponse({'error': 'User Not Found!'}, status=404)
        return JsonResponse(convert_id(user), status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

     
@csrf_exempt    
def get_all_users(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid HTTP method!'}, status=405)

    # Get query parameters
    username = request.GET.get("username")
    email = request.GET.get("email")
    age = request.GET.get("age")

    # Pagination parameters
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        if page < 1 or limit < 1:
            raise ValueError
    except ValueError:
        return JsonResponse({'error': 'Invalid pagination parameters. "page" and "limit" must be positive integers.'}, status=400)

    skip = (page - 1) * limit

    # Build query
    query = {"is_deleted": {"$ne": True}}

    if username:
        query["username"] = {"$regex": username, "$options": "i"}
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    if age:
        try:
            query["age"] = int(age)
        except ValueError:
            return JsonResponse({"error": "Age must be an integer."}, status=400)


    # Fetch filtered users with pagination
    try:
        total = users_collection.count_documents(query)
        users = list(users_collection.find(query).skip(skip).limit(limit))
        data = [convert_id(user) for user in users]

        return JsonResponse({
            "total": total,
            "page": page,
            "limit": limit,
            "users": data
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



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
def render_register_form(request):
    return render(request, "users/registration_form.html")

@csrf_exempt
def register_user_with_picture(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')  
        profile_picture = request.FILES.get('profile_picture')

        if not username or not email or not password:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        profile_picture_path = None
        if profile_picture:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_pics'))
            filename = fs.save(profile_picture.name, profile_picture)
            profile_picture_path = f"profile_pics/{filename}"

        user = {
            "username": username,
            "email": email,
            "password": password,  # 🔒 Hash in production
            "profile_picture": profile_picture_path,
            "is_deleted": False  # default as not deleted
        }

        result = users_collection.insert_one(user)

        try:
            send_mail(
                subject="Welcome to Our Platform!",
                message=f"Hi {username},\n\nThanks for registering with us.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True  
            )
        except Exception as e:
            print(f"Email sending failed: {e}")

        return JsonResponse({
            'message': 'User registered successfully',
            'id': str(result.inserted_id),
            'profile_picture': profile_picture_path
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    
invite_tokens = {}  

@csrf_exempt
def invite_user(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid HTTP method"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)

        # Generate unique invite token
        token = str(uuid.uuid4())
        invite_tokens[token] = email

        # Construct invitation link (you can adjust the frontend route)
        invite_link = f"http://localhost:8000/user-add/?token={token}"

        try:
            send_mail(
                subject="You're invited to register!",
                message=f"Click the link to register: {invite_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True  
            )
        except Exception as e:
            print(f"Email sending failed: {e}")

        return JsonResponse({
            "message": f"Invite sent to {email}",
            "invite_token": token,
            "invite_link": invite_link
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def soft_delete_user(request, id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
    try:
        result = users_collection.update_one({'_id': ObjectId(id)}, {'$set': {'is_deleted': True}})
        if result.matched_count == 0:
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'message': 'User soft deleted'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def restore_user(request, id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
    try:
        result = users_collection.update_one({'_id': ObjectId(id)}, {'$set': {'is_deleted': False}})
        if result.matched_count == 0:
            return JsonResponse({'error': 'User not found'}, status=404)
        return JsonResponse({'message': 'User restored'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)




        
    


