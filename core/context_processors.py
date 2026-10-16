def auth_context(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    return {
        'current_user_id': user_id,
        'current_username': username,
        'is_authenticated': bool(user_id)
    }
