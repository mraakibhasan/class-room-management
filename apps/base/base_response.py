#=== Base Success Response ===#
def base_success_response(message, data=None, pagination=None):
    response = {
        'status': 'success',
        'message': message,
    }
    
    if data is not None:
        response['data'] = data
    
    if pagination is not None:
        response['pagination'] = pagination

    return response

#=== Base Error Response ===#
def base_error_response(message, errors=None):
    response = {
        'status': 'error',
        'message': message,
    }
    
    if errors is not None:
        response['error'] = errors

    return response