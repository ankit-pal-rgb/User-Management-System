import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from bson import ObjectId
from bson.json_util import dumps
from .db_connection import users_collection
from django.views.decorators.csrf import csrf_exempt


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
    if request.method!='GET':
        return JsonResponse({'error' : 'Invalid http method!'}, status=405)
    users = list(users_collection.find())
    data = [convert_id(i) for i in users]
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

        
    


