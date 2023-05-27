from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from contact.models import Contact


def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')


@login_required
def contact_management(request):
    """
    A view to return all messages submitted from users
    """
    # Only superuser's have access to this view
    if not request.user.is_superuser:
        messages.error(
            request,
            'Sorry! Only the team at Easy App can access this.'
        )
        return redirect(reverse('home'))

    contacts = Contact.objects.all()

    context = {
        'contacts': contacts
    }

    return render(request, 'home/contact_management.html', context)


@login_required
def contact_detail(request, contact_id):
    """A view to display the contact message"""
    # Only superuser's have access to this view
    if not request.user.is_superuser:
        messages.error(
            request,
            'Sorry! Only the team at Tarmachan can access this.'
        )
        return redirect(reverse('home'))

    contact = get_object_or_404(Contact, pk=contact_id)

    context = {
        'contact': contact,
    }

    return render(request, 'home/contact_detail.html', context)


@login_required
def delete_contact(request, contact_id):
    """Delete an existing contact message"""
    # Only superuser's have access to this view
    if not request.user.is_superuser:
        messages.error(
            request,
            'Sorry! Only the team at Easy App can access this.'
        )
        return redirect(reverse('home'))
    contact = get_object_or_404(Contact, pk=contact_id)
    contact.delete()
    messages.success(request, f'Contact message {contact.subject} deleted!')
    return redirect(reverse('contact_management'))