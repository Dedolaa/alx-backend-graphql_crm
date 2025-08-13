import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
import django_filters

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
