from crm.models import Customer, Product

Customer.objects.all().delete()
Product.objects.all().delete()

Customer.objects.create(name="Test User", email="test@example.com", phone="+1234567890")
Product.objects.create(name="Laptop", price=999.99, stock=10)
Product.objects.create(name="Mouse", price=19.99, stock=50)

print("Database seeded successfully.")
