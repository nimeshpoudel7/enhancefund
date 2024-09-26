from rest_framework.response import Response

def enhance_response(data=None, message=None, status=None):
    response_data = {
        "code": 1 if status in [200, 201, 204] else 0, 
        "message": message if message else "Request was successful" if status else "Request failed",
        "data": data,
    }
    return Response(response_data, status=status)