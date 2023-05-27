from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q,  Avg
from django.db.models.functions import Lower
from django.http import HttpResponseRedirect

from .models import Product, Category, Comment
from .forms import ProductForm, CommentForm

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    # Gets the product from the database
    product = get_object_or_404(Product, pk=product_id)
    # Gets the comments attached to the product from the database
    # and order so the latest comment appears first
    comments = Comment.objects.filter(
        product_id=product_id).order_by('-create_at')
    # Check to see if there are any comments and updates
    # the product rating based on the average rating
    if comments:
        ratings = comments.count()
        rating_avg = comments.aggregate(Avg('rating'))
        rating = round(rating_avg.get('rating__avg'), 2)
        product.rating = rating
        product.save()
    # if there are no ratings sets product rating to 0
    else:
        ratings = 0
        rating = 0

    context = {
        'product': product,
        'comments': comments,
    }

    return render(request, 'products/product_detail.html', context)



@login_required
def add_product(request):
    """ Add a product to the store """
    # User check as only superusers can add products
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def add_comment(request, product_id):
    """Add a comment"""

    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        # creates a relation with Comment model
        data = Comment()
        # gets the form input data
        data.subject = form['subject'].value()
        data.comment = form['comment'].value()
        data.rating = form['rating'].value()
        data.product_id = product_id
        current_user = request.user
        data.user_id = current_user.id
        # saves the comment
        data.save()
        messages.success(request, 'Successfully added comment!')
        return HttpResponseRedirect(url)
    else:
        form = CommentForm()

    return HttpResponseRedirect(url)


@login_required
def delete_comment(request, comment_id):
    """ Delete an exisiting Comment """

    comment = get_object_or_404(Comment, pk=comment_id)
    product = get_object_or_404(Product, pk=comment.product_id)
    url = request.META.get('HTTP_REFERER')

    # only the user who left the comment or superuser can delete comments
    if request.user == comment.user or request.user.is_superuser:
        comment.delete()
        reviews = Comment.objects.filter(product=product)
        # Updates the product rating when a comment is deleted
        if reviews:
            rating_avg = reviews.aggregate(Avg("rating"))
            rating = round(rating_avg.get('rating__avg'), 2)
            product.rating = rating
        # else sets the product rating to 0
        else:
            product.rating = 0

        product.save()

        messages.success(
            request,
            f'Review {comment.subject} has been deleted!'
        )
        return HttpResponseRedirect(url)
    else:
        messages.error(
            request,
            "Only the team at Tarmachan and the reviewer can access this."
        )
        return HttpResponseRedirect(url)

@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))