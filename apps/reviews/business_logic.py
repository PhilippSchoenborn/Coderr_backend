"""
Business logic for reviews app.
Extracts business logic from views to separate concerns.
"""
from datetime import datetime
from apps.profiles.models import Profile


class ReviewBusinessLogic:
    """Business logic for review operations."""
    
    @staticmethod
    def validate_customer_profile(user):
        """Validate that user has a customer profile."""
        try:
            profile = Profile.objects.get(user=user)
            if profile.type != 'customer':
                return None, "Only customers can create reviews."
            return profile, None
        except Profile.DoesNotExist:
            return None, "Profile not found."
    
    @staticmethod
    def validate_business_user(business_user_id):
        """Validate that business user exists and has business profile."""
        try:
            business_profile = Profile.objects.get(user_id=business_user_id, type='business')
            return business_profile, None
        except Profile.DoesNotExist:
            return None, "Business user not found."
    
    @staticmethod
    def check_existing_review(reviews_list, business_user_id, reviewer_id):
        """Check if reviewer has already reviewed this business user."""
        for review in reviews_list:
            if review['business_user'] == business_user_id and review['reviewer'] == reviewer_id:
                return True
        return False
    
    @staticmethod
    def create_review_data(business_user_id, reviewer_id, rating, description, review_id):
        """Create review data structure."""
        now = datetime.utcnow().isoformat() + 'Z'
        return {
            'id': review_id,
            'business_user': business_user_id,
            'reviewer': reviewer_id,
            'rating': rating,
            'description': description,
            'created_at': now,
            'updated_at': now
        }
    
    @staticmethod
    def filter_reviews(reviews_list, business_user_id=None, reviewer_id=None):
        """Filter reviews by business user or reviewer."""
        filtered = reviews_list
        if business_user_id:
            filtered = [r for r in filtered if str(r.get('business_user')) == str(business_user_id)]
        if reviewer_id:
            filtered = [r for r in filtered if str(r.get('reviewer')) == str(reviewer_id)]
        return filtered
    
    @staticmethod
    def sort_reviews(reviews_list, ordering):
        """Sort reviews by specified field."""
        if ordering == 'updated_at':
            return sorted(reviews_list, key=lambda r: r.get('updated_at', ''), reverse=True)
        elif ordering == 'rating':
            return sorted(reviews_list, key=lambda r: r.get('rating', 0), reverse=True)
        return reviews_list
    
    @staticmethod
    def find_review_by_id(reviews_list, review_id):
        """Find review by ID."""
        return next((r for r in reviews_list if r['id'] == review_id), None)
    
    @staticmethod
    def check_review_ownership(review, user_id):
        """Check if user owns the review."""
        return review['reviewer'] == user_id
    
    @staticmethod
    def update_review_fields(review, update_data, allowed_fields):
        """Update review with allowed fields."""
        updated = False
        for field in allowed_fields:
            if field in update_data:
                review[field] = update_data[field]
                updated = True
        
        if updated:
            review['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        return updated
    
    @staticmethod
    def remove_review_from_list(reviews_list, review_id):
        """Remove review from list by ID."""
        return [r for r in reviews_list if r['id'] != review_id]
