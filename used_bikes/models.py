from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Bikes(models.Model):
    brand=models.CharField(max_length=120)
    name=models.CharField(max_length=120)
    color=models.CharField(max_length=120)
    year=models.PositiveIntegerField
    km_driven=models.CharField(max_length=120)
    price=models.PositiveIntegerField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class BikeImages(models.Model):
    bike=models.ForeignKey(Bikes,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="bike_pics",null=True)

class Offer(models.Model):
    bike=models.ForeignKey(Bikes,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    offered_price=models.PositiveIntegerField()
    options=(
        ("pending","pending"),
        ("approved","approved"),
        ("cancelled","cancelled"),
        ("sold-out","sold-out"),
        ("you bought this bike","you bought this bike")
    )
    status=models.CharField(max_length=120,choices=options,default="pending")

    def __str__(self):
        return str(self.offered_price)


class Sales(models.Model):
    bike=models.OneToOneField(Bikes,on_delete=models.CASCADE)
    seller=models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="s_user")
    buyer=models.ForeignKey(User,on_delete=models.DO_NOTHING,related_name="b_user")
    # sale_price=models.ForeignKey(Offer,on_delete=models.CASCADE)
    sale_price=models.PositiveIntegerField()
    sale_date=models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.bike
