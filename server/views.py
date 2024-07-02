from rest_framework import viewsets
from .models import Server
from .serializers import ServerSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.db.models import Count

class ServerListViewSet(viewsets.ViewSet):
    # Define the initial queryset for the Server model
    queryset = Server.objects.all()
    
    def list(self, request):
        # Get query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"
        
        # Check if the user is authenticated if filtering by user
        if by_user and not request.user.is_authenticated:
            raise AuthenticationFailed()
        
        # Filter the queryset by category if the category parameter is provided
        if category:
            self.queryset = self.queryset.filter(category__name=category)
            
        # Filter the queryset by the authenticated user's ID if by_user is true
        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)
            
        # Annotate the queryset with the number of members if with_num_members is true
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))
        
        # Limit the queryset to the quantity specified by the qty parameter
        if qty:
            self.queryset = self.queryset[:int(qty)]
            
        # Filter the queryset by server ID if the by_serverid parameter is provided
        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                
                # Raise an error if no server with the given ID is found
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
                
            except ValueError:
                # Raise an error if the server ID parameter value is invalid
                raise ValidationError(detail="Server value error")
        
        # Serialize the queryset and include the number of members if specified
        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})
        
        # Return the serialized data as a response
        return Response(serializer.data)
