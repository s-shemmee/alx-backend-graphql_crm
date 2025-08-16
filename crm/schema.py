import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

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

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customerId = graphene.ID(required=True)
    productIds = graphene.List(graphene.ID, required=True)
    orderDate = graphene.DateTime()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def validate_phone(phone):
        if not phone:
            return True
        pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
        return re.match(pattern, phone)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
        if input.phone and not cls.validate_phone(input.phone):
            errors.append("Invalid phone format")
        if errors:
            return CreateCustomer(customer=None, message="Failed", errors=errors)
        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created", errors=None)

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []
        for idx, data in enumerate(input):
            row_errors = []
            if Customer.objects.filter(email=data.email).exists():
                row_errors.append(f"Row {idx+1}: Email already exists")
            if data.phone and not CreateCustomer.validate_phone(data.phone):
                row_errors.append(f"Row {idx+1}: Invalid phone format")
            if row_errors:
                errors.extend(row_errors)
                continue
            customer = Customer.objects.create(
                name=data.name,
                email=data.email,
                phone=data.phone
            )
            created.append(customer)
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        if input.price <= 0:
            errors.append("Price must be positive")
        if input.stock is not None and input.stock < 0:
            errors.append("Stock cannot be negative")
        if errors:
            return CreateProduct(product=None, message="Failed", errors=errors)
        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock if input.stock is not None else 0
        )
        return CreateProduct(product=product, message="Product created", errors=None)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        try:
            customer = Customer.objects.get(pk=input.customerId)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrder(order=None, message="Failed", errors=errors)
        if not input.productIds:
            errors.append("At least one product must be selected")
            return CreateOrder(order=None, message="Failed", errors=errors)
        products = Product.objects.filter(pk__in=input.productIds)
        if products.count() != len(input.productIds):
            errors.append("One or more product IDs are invalid")
            return CreateOrder(order=None, message="Failed", errors=errors)
        total = sum([p.price for p in products])
        order = Order.objects.create(
            customer=customer,
            total_amount=total,
            order_date=input.orderDate if input.orderDate else timezone.now()
        )
        order.products.set(products)
        return CreateOrder(order=order, message="Order created", errors=None)

# Query
class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(graphene.String))

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

# Mutation
class Mutation(graphene.ObjectType):
    createCustomer = CreateCustomer.Field()
    bulkCreateCustomers = BulkCreateCustomers.Field()
    createProduct = CreateProduct.Field()
    createOrder = CreateOrder.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
