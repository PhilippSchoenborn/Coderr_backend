from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReviewSerializer
from .business_logic import ReviewBusinessLogic

REVIEWS = []

class ReviewsListCreateView(APIView):
    """
    API endpoint for listing and creating reviews.
    - GET: Returns a filtered and/or ordered list of all reviews (optionally by business_user, reviewer, or ordering).
    - POST: Allows a customer to create a review for a business user if not already reviewed.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return a list of reviews filtered by business_user_id, reviewer_id, and optionally ordered by 'updated_at' or 'rating'.
        Only accessible for authenticated users.
        """
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        business_user_id = request.query_params.get('business_user_id')
        reviewer_id = request.query_params.get('reviewer_id')
        ordering = request.query_params.get('ordering')
        
        # Filter and sort reviews using business logic
        filtered = ReviewBusinessLogic.filter_reviews(REVIEWS, business_user_id, reviewer_id)
        if ordering in ['updated_at', 'rating']:
            filtered = ReviewBusinessLogic.sort_reviews(filtered, ordering)
        
        return Response(filtered, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new review for a business user by a customer.
        Ensures only one review per customer-business pair and validates business user existence and type.
        Returns 201 on success, 400/401/403/404 on error.
        """
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Validate customer profile
        profile, error = ReviewBusinessLogic.validate_customer_profile(user)
        if error:
            return Response({'detail': error}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            business_user = serializer.validated_data.get('business_user')
            
            # Validate business user
            business_profile, error = ReviewBusinessLogic.validate_business_user(business_user)
            if error:
                return Response({'detail': error}, status=status.HTTP_404_NOT_FOUND)
            
            reviewer = user.id
            
            # Check for existing review
            if ReviewBusinessLogic.check_existing_review(REVIEWS, business_user, reviewer):
                return Response({'detail': 'You have already reviewed this business user.'}, status=status.HTTP_403_FORBIDDEN)
            
            # Create new review
            review = ReviewBusinessLogic.create_review_data(
                business_user, 
                reviewer, 
                serializer.validated_data.get('rating'),
                serializer.validated_data.get('description'),
                len(REVIEWS) + 1
            )
            REVIEWS.append(review)
            return Response(review, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewDetailView(APIView):
    """
    API endpoint for retrieving, updating, and deleting a single review by ID.
    - GET: Returns the review if found.
    - PATCH: Allows the reviewer to update rating/description fields.
    - DELETE: Allows the reviewer to delete their review.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve a single review by its ID. Returns 404 if not found.
        """
        review = ReviewBusinessLogic.find_review_by_id(REVIEWS, pk)
        if review:
            return Response(review, status=status.HTTP_200_OK)
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        """
        Update the rating and/or description of a review if the user is the reviewer.
        Returns 200 on success, 400 if no valid fields, 401/403/404 on error.
        """
        review = ReviewBusinessLogic.find_review_by_id(REVIEWS, pk)
        if not review:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not ReviewBusinessLogic.check_review_ownership(review, request.user.id):
            return Response({'detail': 'You do not have permission to update this review.'}, status=status.HTTP_403_FORBIDDEN)
        
        allowed_fields = ['rating', 'description']
        updated = ReviewBusinessLogic.update_review_fields(review, request.data, allowed_fields)
        
        if updated:
            return Response(review, status=status.HTTP_200_OK)
        return Response({'detail': 'No valid fields to update.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete a review if the user is the reviewer. Returns 204 on success, 401/403/404 on error.
        """
        global REVIEWS
        review = ReviewBusinessLogic.find_review_by_id(REVIEWS, pk)
        if not review:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not ReviewBusinessLogic.check_review_ownership(review, request.user.id):
            return Response({'detail': 'You do not have permission to delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        
        REVIEWS = ReviewBusinessLogic.remove_review_from_list(REVIEWS, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
