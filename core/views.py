from django.shortcuts import render


def landing_page(request):
    """
    Public landing/home page for the Curriculum Management System.
    Accessible to all visitors without requiring authentication.
    """
    return render(request, 'landing.html')
