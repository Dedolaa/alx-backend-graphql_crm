import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import django_filters
from django.db.models import F
from .models import Customer, Product, Order


# =======================
# FILTER CLASSES
# =======================
class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = Customer
        fields = {
            "name": ["icontains", "exact"],
            "email": ["icontains", "exact"],
        }


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            "name": ["icontains", "exact"],
            "price": ["gte", "lte", "exact"],
        }


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            "total_amount": ["gte", "lte", "exact"],
            "order_date": ["gte", "lte", "exact"],
            "customer__name": ["icontains", "exact"],
        }


# =======================
# GRAPHQL TYPES
# =======================
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


# =======================
# QUERY CLASS
# =======================
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    customer = graphene.relay.Node.Field(CustomerType)
    product = graphene.relay.Node.Field(ProductType)
    order = graphene.relay.Node.Field(OrderType)


# =======================
# MUTATIONS
# =======================
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)

    def mutate(self, info, name, email, phone=None):
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        customer = Customer.objects.get(pk=customer_id)
        order = Order(customer=customer)
        order.save()
        order.products.set(Product.objects.filter(pk__in=product_ids))
        order.total_amount = sum([p.price for p in order.products.all()])
        order.save()
        return CreateOrder(order=order)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # No arguments needed for this mutation

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        try:
            # Find products with stock less than 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            if not low_stock_products.exists():
                return UpdateLowStockProducts(
                    success=True,
                    message="No low-stock products found",
                    updated_products=[]
                )
            
            # Update stock by adding 10 to each low-stock product
            updated_count = low_stock_products.update(stock=F('stock') + 10)
            
            # Get the updated products
            updated_products = Product.objects.filter(
                id__in=low_stock_products.values_list('id', flat=True)
            )
            
            return UpdateLowStockProducts(
                success=True,
                message=f"Successfully updated {updated_count} low-stock products",
                updated_products=updated_products
            )
            
        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating low-stock products: {str(e)}",
                updated_products=[]
            )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
    # Add other mutations here...

# Make sure to include the mutation in your schema
schema = graphene.Schema(
    query=Query,  # You should have a Query class defined elsewhere
    mutation=Mutation
)
