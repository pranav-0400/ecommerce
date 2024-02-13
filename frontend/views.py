from django.shortcuts import redirect, render, get_object_or_404
from .models import Item, OrderItem,Order
from django.views.generic import View, DetailView,ListView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.

# def home(request):
#     context={
#         'items':Item.objects.all()
#     }
#     return render(request, 'home.html', context=context)

class HomeView(ListView):
    model=Item
    paginate_by= 12
    template_name='home.html'
    

class ProductDetailView(DetailView):
    model=Item
    template_name='detail.html'
 
@login_required(login_url='../accounts/login')   
def add_to_cart(request, slug):
    item= get_object_or_404(Item, slug=slug)
    
    order_item, created=OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    
    order_q=Order.objects.filter(user=request.user, ordered=False)
    
    if order_q.exists():
        order=order_q[0]
        
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request, "Item added to your cart")
            return redirect('frontend:summary')
        
        else:
            messages.info(request, "Item added to your cart")
            order.items.add(order_item)
            return redirect('frontend:summary')
    else:
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
            
        return redirect('frontend:summary')
    

            
        
@login_required(login_url='../accounts/login')   
def remove_single_item(request, slug):
    item= get_object_or_404(Item, slug=slug)
    
    order_q=Order.objects.filter(user=request.user, ordered=False)
    
    if order_q.exists():
        order=order_q[0]
        
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(item=item,user=request.user, ordered=False)[0]
            if order_item.quantity>1:
                order_item.quantity-=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Cart updated")
            return redirect('frontend:summary')
        
        else:
            messages.info(request, "Item was not in your cart")
            return redirect('frontend:detail' ,slug=slug)
    else:
        
        messages.info(request, "You donot have an active order")
            
        return redirect('frontend:detail', slug=slug)
    

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            current_order=Order.objects.get(user=self.request.user, ordered=False)
            context={
                'object': current_order
            } 
            
            return render(self.request, 'summary.html', context)      
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order") 
            return redirect('/') 
        return render(self.request, 'summary.html') 
    


    
    

