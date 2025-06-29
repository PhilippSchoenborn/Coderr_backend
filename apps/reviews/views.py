from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReviewSerializer
from apps.profiles.models import Profile
from django.contrib.auth.models import User

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
        filtered = REVIEWS
        if business_user_id:
            filtered = [r for r in filtered if str(r.get('business_user')) == str(business_user_id)]
        if reviewer_id:
            filtered = [r for r in filtered if str(r.get('reviewer')) == str(reviewer_id)]
        if ordering in ['updated_at', 'rating']:
            reverse = False
            if ordering == 'updated_at':
                filtered = sorted(filtered, key=lambda r: r.get('updated_at', ''), reverse=True)
            else:
                filtered = sorted(filtered, key=lambda r: r.get('rating', 0), reverse=True)
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
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found.'}, status=status.HTTP_401_UNAUTHORIZED)
        if profile.type != 'customer':
            return Response({'detail': 'Only customers can create reviews.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            business_user = serializer.validated_data.get('business_user')
            # Prüfe, ob business_user existiert und ein Business-Profil ist
            try:
                business_profile = Profile.objects.get(user_id=business_user, type='business')
            except Profile.DoesNotExist:
                return Response({'detail': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
            reviewer = user.id
            for review in REVIEWS:
                if review['business_user'] == business_user and review['reviewer'] == reviewer:
                    return Response({'detail': 'You have already reviewed this business user.'}, status=status.HTTP_403_FORBIDDEN)
            from datetime import datetime
            now = datetime.utcnow().isoformat() + 'Z'
            review = {
                'id': len(REVIEWS) + 1,
                'business_user': business_user,
                'reviewer': reviewer,
                'rating': serializer.validated_data.get('rating'),
                'description': serializer.validated_data.get('description'),
                'created_at': now,
                'updated_at': now
            }
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
        review = self._get_review_by_id(pk)
        if review:
            return Response(review, status=status.HTTP_200_OK)
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        """
        Update the rating and/or description of a review if the user is the reviewer.
        Returns 200 on success, 400 if no valid fields, 401/403/404 on error.
        """
        review = self._get_review_by_id(pk)
        if not review:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        if review['reviewer'] != request.user.id:
            return Response({'detail': 'You do not have permission to update this review.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        allowed_fields = ['rating', 'description']
        updated = False
        for field in allowed_fields:
            if field in data:
                review[field] = data[field]
                updated = True
        from datetime import datetime
        review['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        if updated:
            return Response(review, status=status.HTTP_200_OK)
        return Response({'detail': 'No valid fields to update.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete a review if the user is the reviewer. Returns 204 on success, 401/403/404 on error.
        """
        return self._delete_review(request, pk)

    def _get_review_by_id(self, pk):
        """
        Helper method to retrieve a review from the in-memory REVIEWS list by its ID.
        Returns the review dict or None if not found.
        """
        return next((r for r in REVIEWS if r['id'] == pk), None)

    def _delete_review(self, request, pk):
        """
        Helper method to delete a review from the in-memory REVIEWS list by its ID.
        Checks authentication and reviewer ownership before deletion.
        Returns 204 on success, 401/403/404 on error.
        """
        global REVIEWS
        review = self._get_review_by_id(pk)
        if not review:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        if review['reviewer'] != request.user.id:
            return Response({'detail': 'You do not have permission to delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        REVIEWS = [r for r in REVIEWS if r['id'] != pk]
        return Response(status=status.HTTP_204_NO_CONTENT)
