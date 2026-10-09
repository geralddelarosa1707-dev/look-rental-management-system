import os
from datetime import date
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, flash, redirect, url_for, request, g, session
from werkzeug.security import generate_password_hash

from database import Database
from manager import Manager
from logger import logger
import utils

base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
env_path = os.path.join(base_dir, '.env')

load_dotenv(env_path)

app = Flask(__name__)

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
  raise RuntimeError("SECRET_KEY is not configured.")

app.secret_key = secret_key

def get_manager():
  if "manager" not in g:
    db = Database()
    g.manager = Manager(db)

  return g.manager

def login_required(view):
  @wraps(view)
  def wrapped_view(**kwargs):
    if "user_id" not in session:
      flash("Please login first.", "warning")
      return redirect(url_for("login"))

    return view(**kwargs)

  return wrapped_view

@app.teardown_appcontext
def close_manager_db(exception=None):
  manager_obj = g.pop("manager", None)

  if manager_obj is not None:
    manager_obj.db.close()

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    manager_obj = get_manager()

    email = request.form.get('email', "").strip().lower()
    password = request.form.get('password', "")

    valid_inputs = utils.validate_authentication_input(email, password)

    if not valid_inputs['success']:
      return render_template("authentication/login.html", message=valid_inputs['message'])

    user = manager_obj.get_user(email)

    valid = manager_obj.validation.can_login(user, password)

    if not valid['success']:
      logger.warning(f"LOGIN_FAILED | REASON={valid['log_message']}")

      return render_template("authentication/login.html", message=valid['message'])     

    session['user_id'] = user['user_id']

    flash("Login successfully!", "success")
    return redirect(url_for("home"))

  return render_template("authentication/login.html")

@app.route("/signup", methods=["GET", "POST"])
def create_user():
  if request.method == "POST":
    manager_obj = get_manager()
  
    email = request.form.get('email', "").strip().lower()
    password = request.form.get('password', "")
    confirm_password = request.form.get('confirm_password', "")
  
    valid_inputs = utils.validate_authentication_input(email, password)

    if not valid_inputs['success']:
      return render_template("authentication/signup.html", message=valid_inputs['message'])
  
    valid = manager_obj.validation.can_signup(email, password, confirm_password)

    if not valid['success']:
      logger.warning(f"SIGNUP_FAILED | REASON={valid['log_message']}")
      
      return render_template("authentication/signup.html", message=valid['message'])

    hashed_password = generate_password_hash(password)
  
    manager_obj.signup_user(email, hashed_password)

    logger.info("SIGNUP_SUCCESS")
  
    flash("Signup success. Please login to your account to get started.", "success")
    return redirect(url_for("login"))

  return render_template("authentication/signup.html")

@app.route("/logout")
def logout():
  session.clear()

  return redirect(url_for("login"))

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/add-house", methods=["GET", "POST"])
@login_required
def add_house():
  manager_obj = get_manager()
  
  if request.method == "POST":
    owner_name = request.form.get('owner_name', "").strip().upper()
    house_name = request.form.get('house_name', "").strip().lower()
    house_address = request.form.get('house_address', "").strip().lower()
    monthly_rent = request.form.get('monthly_rent', "").strip()
    bedrooms = request.form.get('bedrooms', "").strip()
    bathrooms = request.form.get('bathrooms', "").strip() 
    house_type = request.form.get('house_type', "").strip().lower()
    
    date_added = date.today().isoformat()

    valid_inputs = utils.validate_add_house_inputs(owner_name, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type)

    if not valid_inputs['success']:
      return render_template(valid_inputs['template'], form_data=request.form, message=valid_inputs['message'])

    monthly_rent = float(monthly_rent)
    bedrooms = int(bedrooms)
    bathrooms = int(bathrooms)
    
    valid = manager_obj.validation.can_add_house(monthly_rent, bedrooms, bathrooms)
            
    if not valid['success']:
      logger.warning(f"ADD_HOUSE_FAILED | REASON={valid['log_message']}")
      return render_template("features/add_house.html", form_data=request.form, message=valid['message'])
              
    house_id = manager_obj.add_house(owner_name, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type, date_added)
            
    logger.info("ADD_HOUSE_SUCCESS")

    flash(f"House ID {house_id} added successfully!", "success")
    return redirect(url_for("home"))

  return render_template("features/add_house.html", form_data={})

@app.route("/rent-house", methods=["GET", "POST"])
@login_required
def rent_house():
  manager_obj = get_manager()
  
  if request.method == "POST":
    house_id = request.form.get('house_id', "").strip()          
    renter_name = request.form.get('renter_name', "").strip().upper()       
    contact_num = request.form.get('contact_num', "").strip()
    rental_duration = request.form.get('rent_duration', "").strip()

    date_rented = date.today().isoformat()

    valid_inputs = utils.validate_rent_house_inputs(house_id, renter_name, contact_num, rental_duration, )

    if not valid_inputs['success']:
      return render_template(valid_inputs['template'], form_data=request.form, message=valid_inputs['message'])

    house_id = int(house_id)
    rental_duration = int(rental_duration)
          
    valid = manager_obj.validation.can_rent_house(house_id, rental_duration)
        
    if not valid['success']:
      logger.warning(f"RENT_HOUSE_FAILED | REASON={valid['log_message']}")
      return render_template("features/rent_house.html", form_data=request.form, message=f"{valid['message']}")
        
    manager_obj.add_rent(house_id, renter_name, contact_num, date_rented, rental_duration)
        
    logger.info("RENT_HOUSE_SUCCESS")

    flash(f"House ID {house_id} rented successfully!", "success")
    return redirect(url_for("home"))

  return render_template("features/rent_house.html", form_data={})
  
@app.route("/rental-history")
@login_required
def rental_history():
  manager_obj = get_manager()
  
  rentals = manager_obj.get_rentals()

  form_data = session.pop("form_data", {})
  
  return render_template("features/rental_history.html", rentals=rentals, form_data=form_data)

@app.route("/return-rental", methods=["POST"])
def return_rental():
  manager_obj = get_manager()
  
  rental_id = request.form.get('rental_id', "").strip()

  valid_input = utils.validate_close_rental_input(rental_id)

  if not valid_input['success']:
    flash(valid_input['message'], valid_input['category'])
    return redirect(url_for(valid_input['view_function']))

  rental_id = int(rental_id)
  closed_date = date.today().isoformat()
          
  valid = manager_obj.validation.can_close_rental(rental_id)
        
  if not valid['success']:
    logger.warning(f"RETURN_HOUSE_FAILED | REASON={valid['log_message']}")
    flash(valid['message'], "warning")
    return redirect(url_for("rental_history"))
          
  rental = manager_obj.get_rental(rental_id)
        
  house_id = rental['house_id']
  
  manager_obj.close_rental(rental_id, closed_date, "RETURNED", cancel_reason=None)
        
  logger.info("RETURN_RENTAL_SUCCESS")

  flash(f"House ID {house_id} returned successfully!", "success")
  return redirect(url_for("rental_history"))

@app.route("/cancel-rental", methods=["POST"])
def cancel_rental():
  manager_obj = get_manager()

  rental_id = request.form.get('rental_id', "").strip()

  valid_input = utils.validate_close_rental_input(rental_id)

  if not valid_input['success']:
    flash(valid_input['message'], valid_input['category'])
    return redirect(url_for(valid_input['view_function']))

  rental_id = int(rental_id)
  closed_date = date.today().isoformat()
        
  cancel_reason = request.form.get('cancel_reason', "").strip().lower()
        
  if not cancel_reason:
    flash("Cancellation reason is required.", "warning")
    session["form_data"] = request.form.to_dict()
    return redirect(url_for("rental_history"))
          
  valid = manager_obj.validation.can_close_rental(rental_id)
        
  if not valid['success']:
    logger.warning(f"CANCEL_HOUSE_FAILED | REASON={valid['log_message']}")
    flash(valid['message'], "warning")
    return redirect(url_for("rental_history"))
        
  rental = manager_obj.get_rental(rental_id)
        
  house_id = rental['house_id']
  
  manager_obj.close_rental(rental_id, closed_date, "CANCELLED", cancel_reason)
        
  logger.info("CANCEL_RENTAL_SUCCESS")

  flash(f"Rental with house ID {house_id} cancelled successfully!", "success")
  return redirect(url_for("rental_history"))

@app.route("/houses")
def houses():
  manager_obj = get_manager()

  houses = manager_obj.get_houses()
        
  return render_template("features/houses.html", houses=houses)

@app.route("/search-house", methods=["POST"])
def search_house():
  manager_obj = get_manager()

  location = request.form.get('location', "").strip().lower()
  house_type = request.form.get('house_type', "").strip().lower()

  try:
    min_bedrooms = utils.optional_int(request.form.get('min_bedrooms', ""))
    min_bathrooms = utils.optional_int(request.form.get('min_bathrooms', ""))
    max_monthly_rent = utils.optional_float(request.form.get('max_monthly_rent', ""))
  except ValueError:
    return render_template("features/houses.html",form_data=request.form,message="Please enter a valid number.", houses=[])

  houses = manager_obj.seek_houses(location, house_type, min_bedrooms,min_bathrooms, max_monthly_rent)

  return render_template("features/houses.html", houses=houses, form_data={})

@app.route("/get-house", methods=["POST"])
def get_house():
  manager_obj = get_manager()
  
  try:
    house_id = int(request.form.get('house_id', "").strip())
  except ValueError:
    return render_template("features/update_house.html", message="Please enter a valid number.", house=None)
        
  house = manager_obj.get_house(house_id)

  if not house:
    return render_template("features/update_house.html", message=f"House ID {house_id} was not found.", house=None)

  return render_template("features/update_house.html", house=house)

@app.route("/update-house", methods=["GET", "POST"])
@login_required
def update_house():
  manager_obj = get_manager()

  if request.method == "POST":
    try:
      house_id = int(request.form.get('house_id', "").strip())
    except ValueError:
      return render_template("features/update_house.html", message="Please enter a valid number.", house=None)
          
    owner = request.form.get('owner', "").strip().upper()
    house_name = request.form.get('house_name', "").strip().lower()
    house_address = request.form.get('house_address', "").strip().lower()
          
    try:
      monthly_rent = utils.optional_float(request.form.get('monthly_rent', ""))
      bedrooms = utils.optional_int(request.form.get('bedrooms', ""))
      bathrooms = utils.optional_int(request.form.get('bathrooms', ""))
    except ValueError:
      return render_template("features/update_house.html", form_data=request.form, message="Please enter a valid number.", house=None)
          
    house_type = request.form.get('house_type', "").strip().lower()
          
    valid = manager_obj.validation.can_update_house(house_id, monthly_rent, bedrooms, bathrooms)
          
    if not valid['success']:
      logger.warning(f"UPDATE_HOUSE_FAILED | REASON={valid['log_message']}")
      return render_template("features/update_house.html", form_data=request.form, message=valid['message'])
          
    manager_obj.patch_house(house_id, owner, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type)
          
    logger.info("UPDATE_HOUSE_SUCCESS")
  
    flash(f"House ID {house_id} updated successfully!", "success")
    return redirect(url_for("home"))

  return render_template("features/update_house.html", house=None, form_data={})

@app.route("/remove-house", methods=["POST"])
def remove_house():
  manager_obj = get_manager()
  
  try:
    house_id = int(request.form.get('house_id', "").strip())
  except ValueError:
    return render_template("features/update_house.html", message="Please enter a valid number.")
          
  valid = manager_obj.validation.can_remove_house(house_id)
        
  if not valid['success']:
    logger.warning(f"REMOVE_HOUSE_FAILED | REASON={valid['log_message']}")
    return render_template("features/update_house.html", message=valid['message'])
          
  manager_obj.delete_house(house_id)
          
  logger.info("REMOVE_HOUSE_SUCCESS")

  flash(f"House ID {house_id} removed successfully!", "success")
  return redirect(url_for("home"))
  
if __name__ == "__main__":
  app.run(debug=True)