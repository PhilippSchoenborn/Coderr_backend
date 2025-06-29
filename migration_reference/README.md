# Django Migrations Reference from Old API

This directory contains copies of the original migrations from the old `api` app for reference purposes.

## Important Migration Files:

### 0001_initial.py
- Creates the initial Profile model

### 0002_offer.py  
- Creates the Offer model

### 0005_order.py
- Creates the Order model

### 0006_alter_profile_file_offerdetail_order_offer_detail.py
- Adds OfferDetail model and updates Profile.file field

### 0007_rename_image_offer_file_alter_offerdetail_features_and_more.py
- Renames Offer.image to Offer.file and updates OfferDetail fields

## Note:
When creating new migrations for the modular structure, refer to these files for the correct field definitions and relationships.

The new apps should create their own migrations that recreate the same database structure but within the new app namespaces.
