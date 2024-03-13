from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template import loader
from Sellerapp.models import *
from Userapp.models import *
from Adminapp.models import *
from Userapp.models import UserAddress, UserCart
from django.db.models import Q, Sum, F
from decimal import Decimal
# from .models import RecentlyViewedProduct
from django.http import JsonResponse


def home_page(request):
    data = Product.objects.select_related('seller_id').prefetch_related('images').all()
    cat = Category.objects.all()

    categorized_products = {}
    for y in cat:
        category_products = data.filter(main_category_id=y.main_category_id)
        if category_products.exists():
            categorized_products[y.main_category_name] = category_products
    print(data.values())

    # if request.user.is_authenticated:
    #     recently_viewed_products = RecentlyViewedProduct.objects.filter(email=request.user)
    # else:
    #     recently_viewed_products = None

    # recently_viewed_id = request.session.get('recently_viewed', [])
    # recently_viewed_products = Product.objects.filter(product_id__in=recently_viewed_id)
    # if 'product_id' in request.GET:
    #     product_id = request.GET.get('product_id')
    #     if product_id in recently_viewed_id:
    #         recently_viewed_id.append(product_id)
    #         request.session['recently_viewed'] = recently_viewed_id

    users = 'no user'
    if 'user' in request.session:
        current_user = request.session['user']
        users = User.objects.get(email=current_user)

    if request.user.is_authenticated:
        recently_viewed_products = Product.objects.filter(seller_id=request.user.id)
    else:
        recently_viewed_products = Product.objects.all()

    return render(request, 'homepage.html',{'products': data, 'user': users, 'cat': cat, 'categorized_products': categorized_products,'recently_viewed_products': recently_viewed_products})


def products(request, id):
    print("dcfvgbhnjm")
    data = Product.objects.select_related('seller_id').prefetch_related('images').filter(product_id=id)
    print(data.values())
    datas = ReviewRating.objects.filter(product_id=Product.objects.get(product_id=id))
    if 'user' in request.session:
        print("sdfghjvbnhj")
        email = request.session.get('user')
        print(data.values())
        print(f'user : {email}')

        if request.method == 'POST':
            print('cart now')
            quantity = request.POST.get('quantity')
            cart_data = UserCart()
            cart_data.product_id = Product.objects.get(product_id=id)
            cart_data.quantity = quantity
            cart_data.user_id = User.objects.get(email=email)
            cart_data.save()
            return redirect('/cart')

        # if request.user.is_authenticated:
        #     RecentlyViewedProduct.objects.create(email=request.user, product=data)

    return render(request, 'single-product.html', {'products': data, 'review': datas})


def cart(request):
    print("sdfghj")
    data = Product.objects.select_related('seller_id').prefetch_related('images').filter(product_id=id)
    print(data.values())
    # product = Product.objects.filter(product_id=request.POST.get('product_id'))
    if 'user' in request.session:
        print("sdfghjvbnhj")
        email = request.session.get('user')
        print(data.values())
        print(f'user : {email}')
        # cart_items = UserCart.objects.filter(user_id=User.objects.get(email=request.session.get('user')))
        # total_price = cart_items.aggregate(total_price=Sum('product_id__price' * 'quantity'))
        #
        # email = request.session.get('user')
        # data = UserCart.objects.filter(user_id=User.objects.get(email=email))
        # total_price = sum(item.product_id.price * item.quantity for item in data)
        # print(f' total: {total_price}')
        user_cart_items = UserCart.objects.filter(user_id=request.user)
        total_price = sum(item.product_id.price * item.quantity for item in user_cart_items)

        if request.method == 'POST':

            qty = int(request.POST['quantity'])

            product_id = int(request.POST["product_id"])

            cart_obj = UserCart()
            cart_obj.product_id = Product.objects.get(product_id=product_id)
            cart_obj.quantity = qty
            cart_obj.user_id = User.objects.get(email=request.session.get('user'))
            cart_obj.save()

        email = request.session.get('user')

        data = UserCart.objects.filter(user_id=User.objects.get(email=email))
        print(data.values())
        return render(request, 'cart.html', {'user_cart_items': user_cart_items,'cart': data})
    else:
        return redirect('/login')


# def cart(request):
#     if 'user' in request.session:
#         print("sdfghjvbnhj")
#         email = request.session.get('user')
#         print(f'user : {email}')
#         user_id = User.objects.get(email=request.session.get('user'))
#         if request.method == "POST":
#             print("aaaa")
#
#             qty = request.POST['quantity']
#
#             product_id = request.POST["product_id"]
#             product_details = Product.objects.get(product_id=product_id)
#             if not UserCart.objects.filter(product_id=product_id,user_id=user_id).exists():
#                 cartdata = UserCart(product_id=product_id,user_id=user_id,quantity=qty)
#                 cartdata.save()
#                 usercartdetails = UserCart.objects.filter(user_id=user_id)
#                 return render("cart.html",{'user_cart_items':usercartdetails})
#             else:
#                 usercartdetails = UserCart.objects.filter(user_id=user_id)
#                 total_price = sum(item.product_id.price * item.quantity for item in usercartdetails)
#                 return render("cart.html",{'user_cart_items':usercartdetails,'total_price':total_price})
#         else:
#             usercartdetails = UserCart.objects.filter(user_id=UserCart.objects.get(email=email))
#         return render("cart.html", {'user_cart_items': usercartdetails})
#     else:
#         return redirect('/login')


def buy(request):
    if 'user' in request.session:
        email = request.session.get('user')
        print("aaaaaaaaaaaaaaaaaaaaaa")
        product_details=Order.objects.filter(user_id=User.objects.get(user_id=request.session('user')))
        total_price = UserCart.objects.filter(user_id=User.objects.get(email=request.session.get('user'))).aggregate(
            total_price=Sum(F('product_id__price') * F('quantity'), output_field=models.DecimalField())
            )['total_price'] or Decimal('0.00')
        print(f"Total price for user : ₹{total_price}")
        address = UserAddress.objects.all()

        # data = Cart.objects.filter(user_id=User.objects.get(email=email))
        # print(data.values())

        # amount = 0
        # for x in cart:
        #     value = x.quantity * x.product_id.price
        #     amount = amount + value
        #     total_price = amount + 50

        data = UserCart.objects.filter(user_id=User.objects.get(email=email))
        return render(request, 'buynow.html', {'cart': data,'total_price': total_price,'address': address})
    else:
        return redirect('/login')


def checkout(request):
    if 'user' in request.session:
        email = request.session.get('user')
        data = UserAddress.objects.filter(user_id=User.objects.get(email=email))
        return render(request, 'checkout.html', {'cart': data})


def dlt_product(request, cart_id):
    print("rtttttttttttttttttttttttttttttt")
    data = UserCart.objects.get(cart_id=cart_id)
    data.delete()
    return redirect('/cart')


def category(request, main_category_id):
    print(main_category_id)
    print("category function")
    data = Category.objects.get(main_category_id=main_category_id)
    data1 = Product.objects.select_related('seller_id').prefetch_related('images').all()
    print(data)
    data1 = Product.objects.filter(main_category_id=data)
    cat = Category.objects.all()
    print(data1.values())
    if request.method == 'POST':
        search = request.POST.get('search')
        if 'selected_price' in request.POST:
            print(int(request.POST['selected_price']))
            data1 = data1.filter(price__lt=int(request.POST['selected_price']))
        if 'selected_discount' in request.POST:
            print(int(request.POST['selected_discount']))
            data1 = data1.filter(offer__discount__lt=int(request.POST['selected_discount']))
        data1 = data1.prefetch_related('images')
        print(data1.values())
    return render(request, 'category.html', {'category': data1, 'cat': cat, 'products': data, })


def search(request):
    print("rrrrrrrrr")
    data = Product.objects.select_related('seller_id').prefetch_related('images').all()

    offer = Offer.objects.all()
    cat = Category.objects.all()
    print(request.method)
    brand_id = request.GET.get('brand_id')
    print(brand_id)
    # offer_id = request.GET.get('offer_id')
    # print(offer_id)
    search = ''
    if brand_id:
        print('hello')

        data = Product.objects.filter(brand_id=Brand.objects.get(brand_id=brand_id))
        # data1 = Product.objects.filter(offer_id=Offer.objects.get(offer_id=offer_id))
    if request.method == 'POST':
        search = request.POST.get('search')
        if request.POST.get('search'):
            data = data.filter(Q(product_name__icontains=search) | Q(description__icontains=search) | Q(price__icontains=search) | Q(main_category_id__main_category_name__icontains=search) | Q(brand_id__brand_name__icontains=search))
            # data1 = data1.filter(Q(offer_id__offer_name__icontains=search) | Q(offer_id__discount__icontains=search))
            # print(data1.values())
        if 'selected_price' in request.POST:
            print(int(request.POST['selected_price']))
            data = data.filter(price__lt=int(request.POST['selected_price']))
        if 'selected_discount' in request.POST:
            print(int(request.POST['selected_discount']))
            data = data.filter(offer__discount__lt=int(request.POST['selected_discount']))
            data = data.prefetch_related('images')
            print(data.values())

    return render(request, 'search.html', {'products': data, 'cat': cat, 'search':search, 'brands': brand})


def brand(request):
    data = Brand.objects.all()
    cat = Category.objects.all()
    print(data.values())
    return render(request, 'brand.html', {'datas': data, 'cat': cat})

def all_brands(request):
    data = Brand.objects.all()
    print(data.values())
    return render(request, 'all-brand.html')


def wishlist(request):
    print("qwwwwwwwwwwwwwwwwwwwwww")
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        print(f'product : {product_id}')
        if 'user' in request.session:
            user_id = request.session['user']
            wishlist_item = Wishlist.objects.filter(email=User.objects.get(user_id=request.session['user']),product_id=Product.objects.get(product_id=product_id))
            if wishlist_item.exists():
                print('Product already in wishlist.')
                return JsonResponse({'success': True, 'message': 'Product already in wishlist.'})
            else:
                print('Product added to wishlist.')
                wishlist_item = Wishlist.objects.create(user_id=User.objects.get(user_name=request.session['user']),product_id=Product.objects.get(Product_id=product_id))
                wishlist_item.save()
                return JsonResponse({'success': True, 'message': 'Product added to wishlist.'})
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success':False})

    #     return JsonResponse({'message': 'Product added to wishlist successfully!'})
    # else:
    #     return JsonResponse({'error': 'Invalid request method'})


    # if 'user' in request.session:
    #     email = request.session.get('user')
    #     data = Wishlist.objects.filter(user_id=User.objects.get(email=request.session['user']))
    #     print(data.values())
    #     return render(request, 'wishlist.html', {'wishlist': data})
    # else:
    #     return redirect('/login')


def dlt_listproduct(request, list_id):
    print("rtttttttttttttttttttttttttttttt")
    data = Wishlist.objects.get(list_id=list_id)
    data.delete()
    return redirect('/wishlist')


def offers(request):
    events = Event.objects.all()
    cat = Category.objects.all()
    data = Product.objects.select_related('product_id').prefetch_related('images').all()
    return render(request, 'offers.html', {'events': events, 'cat': cat, 'event.offer_set.all': data})


def reviewrating(request,product_id):
    print(product_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        print(rating, review)
        data = ReviewRating()
        data.rating = rating
        data.review = review
        data.user_id = User.objects.get(email=request.session['user'])
        data.product_id = Product.objects.get(product_id=product_id)
        data.save()
        print("Review successfully  added.............!")
        return redirect(f'/products/{product_id}')
    else:
        pass


def signup(request):
    if request.method == "POST":
        username = request.POST.get('user_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        print(username, email, phone_number, password)
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'invalid'})
        else:
            data = User(user_name=username, email=email, phone_number=phone_number, password=password)
            data.save()
            print("signup successfully .............!")
            return redirect('/login')
    else:
        return render(request, 'signup.html')


def login(request):
    if request.method == "POST":
        email1 = request.POST.get('email')
        password1 = request.POST.get('password')
        data = User.objects.filter(email=email1, password=password1)
        if data is not None:
            request.session['user'] = email1
            print('login successfully ..............!')
            return redirect('/')
        else:
            print('invalid')
            return render(request, 'login.html', {'error_message': 'Invalid email_id or password'})
    return render(request, 'login.html')


def profile(request):
    if 'user' in request.session:
        data1 = request.session['user']
        print(data1)
        data = User.objects.filter(email=data1)
        user_image = UserImage.objects.filter(user_id=User.objects.get(email=data1)).first()
        print(user_image)
        return render(request, 'profile.html', {'data': data, 'user_image': user_image})
    else:
        return redirect('/login')


def view_address(request):
    print('address Function called')
    if 'user' in request.session:
        data = UserAddress.objects.filter(user_id=User.objects.get(email=request.session['user']))
        return render(request, 'view_address.html', {'data': data})
    else:
        return redirect('/login')


def address(request):
    if 'user' in request.session:
        email = request.session.get('user')
        print(email)
        if request.method == "POST":
            house_id = request.POST.get('house_id')
            house_name = request.POST.get('house_name')
            house_number = request.POST.get('house_number')
            place = request.POST.get('place')
            post = request.POST.get('post')
            pin = request.POST.get('pin')
            landmark = request.POST.get('landmark')
            city = request.POST.get('city')
            print(house_id, house_id, house_name, house_number, place, post, pin, landmark, city)
            print(User.objects.filter(email=email))
            data = UserAddress()
            data.house_name = house_name
            data.house_number = house_number
            data.place = place
            data.post = post
            data.pin = pin
            data.landmark = landmark
            data.city = city
            data.user_id = User.objects.get(email=email)
            data.city_name = LocationCity.objects.get(city_name=city)
            data.save()
            print("Address successfully  added .............!")
            return redirect('profile')
        return render(request, 'address.html')
    else:
        return redirect('login')


def edit_address(request, house_id):
    data = UserAddress.objects.filter(house_id=house_id)
    if 'user' in request.session:
        email = request.session.get('user')
        if request.method == 'POST':
            house_name = request.POST.get('house_name')
            house_number = request.POST.get('house_number')
            place = request.POST.get('place')
            post = request.POST.get('post')
            pin = request.POST.get('pin')
            landmark = request.POST.get('landmark')
            city = request.POST.get('city')
            print(house_id, house_id, house_name, house_number, place, post, pin, landmark, city)
            data = UserAddress.objects.get(house_id=house_id)
            data.house_name = house_name
            data.house_number = house_number
            data.place = place
            data.post = post
            data.pin = pin
            data.landmark = landmark
            data.city = city
            data.user_id = User.objects.get(email=email)
            data.city_name = LocationCity.objects.get(city_name=city)
            data.save()
            print("Address successfully  added .............!")
            return redirect('view_address')

        return render(request, 'edit_address.html', {'data': data})
    else:
        return redirect('login')


def dlt_address(request, house_id):
    print("rtttttttttttttttttttttttttttttt")
    data = UserAddress.objects.get(house_id=house_id)
    data.delete()
    return redirect('view_address')


def buy(request, house_id=None):
    print("xxxxxxxxxxx")
    if 'user' in request.session:
        email = request.session.get('user')
        if request.method == 'POST':
            address = UserAddress.objects.filter(house_id=house_id)
            print(address.values())
        return render(request, 'buynow.html')
    else:
        return redirect('/login')


def logout(request):
    del request.session['user']
    return redirect('/login')
