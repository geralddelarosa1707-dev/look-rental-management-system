from werkzeug.security import check_password_hash
from email_validator import validate_email, EmailNotValidError

from database import Database
import utils

def return_message(success, message, log_message):
  return {
    "success": success,
    "message": message,
    "log_message": log_message
  }

class Manager:
  def __init__(self, db):
    self.db = db
    self.validation = Validation(self.db)

  def get_user(self, email):
    user = self.db.get_user_by_email(email)

    return user

  def signup_user(self, email, password):
    self.db.create_user(email, password)
    
  def add_house(self, owner_name, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type, date_added):
    return self.db.insert_house(owner_name, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type, date_added)
  
  def add_rent(self, house_id, renter_name, contact_num, date_rented, rental_duration):
    self.db.rent_house_status(house_id)
    
    self.db.insert_rental(house_id, renter_name, contact_num, date_rented, rental_duration)
  
  def close_rental(self, rental_id, closed_date, action, cancel_reason):
    rental = self.db.get_rental_by_id(rental_id)
    
    house_id = rental['house_id']
    
    self.db.update_rental_status(rental_id, closed_date, action, cancel_reason)
    
    self.db.avail_house_status(house_id)

  def get_houses(self):
    return self.db.show_houses()

  def seek_houses(self, location, house_type, min_bedrooms, min_bathrooms, max_monthly_rent):
    return self.db.search_houses(location, house_type, min_bedrooms, min_bathrooms, max_monthly_rent)
    
  def get_rental(self, rental_id):
    return self.db.get_rental_by_id(rental_id)

  def get_rentals(self):
    return self.db.show_rentals()

  def get_house(self, house_id):
    return self.db.show_house(house_id)

  def patch_house(self, house_id, owner, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type):    
    self.db.update_house(house_id, owner, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type)

  def delete_house(self, house_id):
    self.db.remove_house(house_id)

    self.db.not_avail_house_status(house_id)
    
class Validation:
  def __init__(self, db):
    self.db = db

  def can_login(self, user, password):
    if not user:
      return return_message(False, "Invalid email or password.", "INVALID_EMAIL_OR_PASSWORD")

    if not check_password_hash(user["password"], password):
      return return_message(False, "Invalid email or password.", "INVALID_EMAIL_OR_PASSWORD")

    return return_message(True, None, None)

  def can_signup(self, email, password, confirm_password):
    try:
      email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
      return return_message(False, "Invalid email address.", "INVALID_EMAIL")
      
    user = self.db.get_user_by_email(email)

    if user:
      return return_message(False, "Unable to create your account. Please check your information or use another email.", "USER_ALREADY_EXIST")

    if len(password) < 8:
      return return_message(False, "Password must be at least 8 characters.", "INVALID_PASSWORD")

    if password != confirm_password:
      return return_message(False, "Password do not match.", "INVALID_PASSWORD")

    return return_message(True, None, None)

  @staticmethod
  def can_add_house(monthly_rent, bedrooms, bathrooms):
    if monthly_rent < 1:
      return return_message(False, "Monthly rent must be greater than 0.", "INVALID_NUMBER_OF_RENT")
  
    if bedrooms < 1:
      return return_message(False, "House must at least have 1 bedroom.", "INVALID_NUMBER_OF_BEDROOMS")
  
    if bathrooms < 1:
      return return_message(False, "House must at least have 1 bathroom.", "INVALID_NUMBER_OF_BATHROOMS")
      
    return return_message(True, "", "")
    
  def can_rent_house(self, house_id, rental_duration):
    house = self.db.get_house_by_id(house_id)
  
    if house is None:
      return return_message(False, "House ID does not exist.", "HOUSE_NOT_EXIST")
      
    if house['availability'] == "NOT AVAILABLE":
      return return_message(False, "House is not available.", None)
      
    if house['availability'] != "AVAILABLE":
      return return_message(False, "House is currently rented.", None)
      
    if rental_duration < 1:
      return return_message(False, "Rental duration must be at least 1 month.", "INVALID_NUMBER_OF_RENTAL_DURATION")
    
    return return_message(True, "", "")
    
  def can_close_rental(self, rental_id):
    rented = self.db.get_rental_by_id(rental_id)
    
    if rented is None:
      return return_message(False, "Rental ID does not exist.", "RENTAL_ID_NOT_EXIST")
    
    if rented["status"] != "ACTIVE":
      return return_message(False, "Rental is already closed.", "HOUSE_NOT_ACTIVE")
      
    return return_message(True, "", "")
    
  def can_update_house(self, house_id, monthly_rent, bedrooms, bathrooms):
    house = self.db.get_house_by_id(house_id)
    
    if house is None:
      return return_message(False, "House ID does not exist.", "HOUSE_NOT_EXIST")
      
    if house['availability'] == "NOT AVAILABLE":
      return return_message(False, "House is not available.", None)
      
    if house["availability"] != "AVAILABLE":
      return return_message(False, "House is currently rented.", None)
  
    if monthly_rent is not None and monthly_rent < 1:
      return return_message(False, "Monthly rent must be at least greater than 0", "INVALID_NUMBER_OF_RENT")
    
    if bedrooms is not None and bedrooms < 1:
      return return_message(False, "House must at least have 1 bedroom.", "INVALID_NUMBER_OF_BEDROOMS")
    
    if bathrooms is not None and bathrooms < 1:
      return return_message(False, "House must at least have 1 bathroom.", "INVALID_NUMBER_OF_BATHROOMS")
    
    return return_message(True, "", "")
    
  def can_remove_house(self, house_id):
    house = self.db.get_house_by_id(house_id)
    
    if house is None:
      return return_message(False, "House ID does not exist.", "HOUSE_NOT_EXIST")
      
    if house["availability"] != "AVAILABLE":
      return return_message(False, "House is currently rented.", None)
      
    return return_message(True, "", "")