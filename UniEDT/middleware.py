from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Apps nécessitant une connexion
        self.protected_apps = ['enseignants', 'events', 'programmation']

    def __call__(self, request):
        path = request.path
        if any(path.startswith('/' + app) for app in self.protected_apps):
            if not request.session.get('user'):
                return redirect('login')  # adapte selon tes urls.py
        response = self.get_response(request)
        return response
