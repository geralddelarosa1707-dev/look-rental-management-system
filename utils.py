def return_render_template(success, template, message):
  return {
    "success": success,
    "template": template,
    "message": message
  }

def return_redirect(success, message, category, view_function):
  return {
    "success": success,
    "message": message,
    "category": category,
    "view_function": view_function
  }

def validate_authentication_input(email, password):
  if not email:
    return return_render_template(False, None, "Email is required.")

  if not password:
    return return_render_template(False, None, "Password is required.")

  return return_render_template(True, None, None)

def validate_add_house_inputs(owner_name, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type):
  if not owner_name:
    return return_render_template(False, "features/add_house.html", "Owner name is required")

  if not house_name:
    return return_render_template(False, "features/add_house.html", "House name is required.")

  if not house_address:
    return return_render_template(False, "features/add_house.html", "House address is required.")

  if not monthly_rent:
    return return_render_template(False, "features/add_house.html", "Monthly Rent is required.")

  try:
    monthly_rent = float(monthly_rent)
  except ValueError:
    return return_render_template(False, "features/add_house.html", "Please enter a valid number.")

  if not bedrooms:
    return return_render_template(False, "features/add_house.html", "No. of bedrooms is required.")
              
  try:
    bedrooms = int(bedrooms)
  except ValueError:
    return return_render_template(False, "features/add_house.html", "Please enter a valid number.")

  if not bathrooms:
    return return_render_template(False, "features/add_house.html", "No. of bathrooms is required.")
              
  try:
    bathrooms = int(bathrooms)
  except ValueError:
    return return_render_template(False, "features/add_house.html", "Please enter a valid number.")

  if not house_type:
    return return_render_template(False, "features/add_house.html", "Please enter a house type.")

  return return_render_template(True, None, None)

def validate_rent_house_inputs(house_id, renter_name, contact_num, rental_duration, ):
  if not house_id:
    return return_render_template(False, "features/rent_house.html", "House ID is required.")
    
  try:
    house_id = int(house_id)
  except ValueError:
    return return_render_template(False, "features/rent_house.html", "Please enter a valid number.")

  if not renter_name:
    return return_render_template(False, "features/rent_house.html", "Renter name is required.")

  if not contact_num:
    return return_render_template(False, "features/rent_house.html", "Contact number is required.")

  if not rental_duration:
    return return_render_template(False, "features/rent_house.html", "Rental duration is required.")
        
  try:
    rental_duration = int(rental_duration)
  except ValueError:
    return return_render_template(False, "features/rent_house.html", "Please enter a valid number.")

  return return_render_template(True, None, None)

def validate_close_rental_input(rental_id):
  if not rental_id:
    return return_redirect(False, "Rental ID is required.", "warning", "rental_history")
  
  try:
    rental_id = int(rental_id)
  except ValueError:
    return return_redirect(False, "Please enter a valid number.", "warning", "rental_history")

  return return_redirect(True, None, None, None)

def optional_int(value):
  value = value.strip()

  if not value:
    return None

  return int(value)
    
def optional_float(value):
  value = value.strip()

  if not value:
    return None

  return float(value)