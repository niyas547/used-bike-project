from django.shortcuts import render
from used_bikes.serializers import UserSerializer,BikeSerializer,BikeImageSerializer,OfferSerializer,SalesSerializer
from rest_framework.viewsets import ModelViewSet,ViewSet
from rest_framework.response import Response
from used_bikes.models import Bikes,BikeImages,Offer,Sales
from rest_framework.decorators import action
from rest_framework import permissions


# Create your views here.

class UsersView(ViewSet):
    def create(self,request,*args,**kwargs):
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)

class BikeView(ViewSet):
    # to create bike-localhost:8000/olx/bikes/    pass bike details POST request
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def create(self,request,*args,**kwargs):
        serializer=BikeSerializer(data=request.data,context={"user":request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    #to list all bikes-localhost:8000/olx/bikes/ GET request
    def list(self,request,*args,**kwargs):
        all_bikes=Bikes.objects.all()
        active_bikes=[ bike for bike in all_bikes if bike.is_active]
        serializer=BikeSerializer(active_bikes,many=True)
        return Response(data=serializer.data)
    #to get a specific bike details-localhost:8000/olx/bikes/{id}/  GET request
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        bike=Bikes.objects.get(id=id)
        if bike.is_active:
            serializer=BikeSerializer(bike)
            return Response(data=serializer.data)
        else:
            return Response({"message":"not found"})
    #to update a specific bike-localhost:8000/olx/bikes/{id}  PUT request Bike updating details
    def update(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        bike=Bikes.objects.get(id=id)
        serializer=BikeSerializer(instance=bike,data=request.data)
        if bike.user==request.user:
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)
        else:
            return Response(data="invalid user")
    #to delete a specific bike-localhost:8000/olx/bikes/{id}/ DELETE request
    def destroy(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        bike=Bikes.objects.get(id=id)
        current_user=request.user
        if bike.user==current_user:
            bike.delete()
            return Response({"message":"deleted"})
        else:
            return Response({"message":"invalid user"})
    @action(methods=["POST"],detail=True)
    #to add images to a specific bike-localhost:8000/olx/bikes/{id}/add_images/ POST request pass images
    def add_images(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        bike=Bikes.objects.get(id=id)
        if bike.user==request.user:
            image_count=bike.bikeimages_set.all().count()
            if image_count<5:
                serializer=BikeImageSerializer(data=request.data,context={"bike":bike})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data)
                else:
                    return Response(data=serializer.errors)
            else:
                return Response({"message":"you can only add 5 images"})
        else:
            return Response({"message":"invalid user!!!!"})

    # to get images of specific bike-localhost:8000/olx/bikes/{id}/get_images/ GET request
    @action(methods=["GET"],detail=True)
    def get_images(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        bike=Bikes.objects.get(id=id)
        if bike.is_active:
            bike_images=bike.bikeimages_set.all()
            serializer=BikeImageSerializer(bike_images,many=True)
            return Response(data=serializer.data)
        else:
            return Response({"message":"no active bike"})

    #to make offer for a bike by the buyer-localhost:8000/olx/bikes/{id}/make_offer/ POST request pass offered_price
    @action(methods=['POST'], detail=True)
    def make_offer(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        offers = bike.offer_set.all()
        buyer = [offer.user for offer in offers if offer.user == request.user]
        if bike.is_active and bike.user != request.user:
            if not buyer:
                serializer = OfferSerializer(data=request.data, context={'bike': bike, 'user': request.user})
                if serializer.is_valid():
                    serializer.save()
                    return Response(data=serializer.data)
                else:
                    return Response(data=serializer.errors)
            else:
                return Response(data={'msg': 'one user can make only one offer'})
        else:
            return Response(data={'msg': 'not allowed'})

    # seller can see offers for his add-localhost:8000/olx/bikes/{id}/offer_requests/ GET request
    @action(methods=['GET'], detail=True)
    def offer_requests(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        if bike.is_active:
            offers = bike.offer_set.all()
            if bike.user == request.user:
                serializer = OfferSerializer(offers, many=True)
                return Response(data=serializer.data)
            else:
                return Response(data={'msg': 'Access denied'})
        else:
            return Response(data={'msg': 'Bike not found'})

    @action(methods=['POST'], detail=True)
    def mark_as_sold(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        bike = Bikes.objects.get(id=id)
        seller = bike.user
        approved_offer = bike.offer_set.get(status='approved')
        buyer = approved_offer.user
        sale_price = approved_offer.offered_price
        remaining_offers = bike.offer_set.all().exclude(id=approved_offer.id)
        if request.user == seller:
            serializer = SalesSerializer(data=request.data, context={'bike': bike,
                                                                     'seller': seller,
                                                                     'buyer': buyer,
                                                                     'sale_price': sale_price,
                                                                     })
            if serializer.is_valid():
                serializer.save()
                bike.is_active = False
                bike.save()
                for offer in remaining_offers:
                    offer.status = 'sold-out'
                    offer.save()
                approved_offer.status = 'you bought this product'
                approved_offer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)

        else:
            return Response(data='invalid user')

        # --------------Buyer can view the offers list----------------
class BuyersView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]


    def list(self, request, *args, **kwargs):

        offers = Offer.objects.filter(user=request.user)
        serializer = OfferSerializer(offers, many=True)
        return Response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        if offer.user == request.user:
            serializer = OfferSerializer(offer)
            return Response(data=serializer.data)
        else:
            return Response({'msg': 'not found'})

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        if offer.user == request.user and offer.bike.is_active:
            serializer = OfferSerializer(instance=offer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                offer.status = 'pending'
                offer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)
        else:
            return Response(data={'msg': 'not allowed'})

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        if offer.user == request.user:
            offer.delete()
            return Response(data={'msg': 'Deleted'})
        else:
            return Response({'msg': 'invalid user login'})

class ReviewOfferRequestsView(ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        bike = offer.bike
        seller = offer.bike.user
        buyer = offer.user
        if seller == request.user:
            serializer = OfferSerializer(offer)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'invalid user login'})

    @action(methods=['POST'], detail=True)
    def accept_offer(self, request, *args, **kwargs):

        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        bike = offer.bike
        remaining_offers = bike.offer_set.all().exclude(id=id)
        seller = offer.bike.user
        if request.user == seller:
            offer.status = 'approved'
            offer.save()
            for ofr in remaining_offers:
                ofr.status = 'cancelled'
                ofr.save()
            serializer = OfferSerializer(offer)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'invalid user'})

    @action(methods=['POST'], detail=True)
    def cancel_offer(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        offer = Offer.objects.get(id=id)
        bike_owner = offer.bike.user
        if request.user == bike_owner:
            offer.status = 'cancelled'
            offer.save()
            cancelled_offer = Offer.objects.get(id=id)
            serializer = OfferSerializer(cancelled_offer)
            return Response(data=serializer.data)
        else:
            return Response(data={'msg': 'You have no access to this functionality'})



class SalesView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['GET'], detail=False)
    def sold_bikes(self, request, *args, **kwargs):
        bikes = Sales.objects.filter(seller=request.user)
        serializer = SalesSerializer(bikes, many=True)
        return Response(data=serializer.data)

    @action(methods=['GET'], detail=False)
    def bought_bikes(self, request, *args, **kwargs):
        bikes = Sales.objects.filter(buyer=request.user)
        serializer = SalesSerializer(bikes, many=True)
        return Response(data=serializer.data)