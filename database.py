import sqlite3
import os

class Database:
  def __init__(self):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "rent.db")
    
    self.conn = sqlite3.connect(db_path)
    self.conn.row_factory = sqlite3.Row
    self.conn.execute("PRAGMA foreign_keys = ON")
    
    self.cursor = self.conn.cursor()

    self.create_user_table()
    self.create_house_table()
    self.create_rental_table()

  def close(self):
    self.conn.close()

  def create_user_table(self):
    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'TENANT'
    );
    """)

    self.conn.commit()
  
  def create_house_table(self):
    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS Houses (
    house_id INTEGER PRIMARY KEY,
    owner_name TEXT NOT NULL,
    house_name TEXT NOT NULL,
    house_address TEXT NOT NULL,
    monthly_rent REAL NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    house_type TEXT NOT NULL,
    date_added TEXT NOT NULL,
    availability TEXT NOT NULL DEFAULT 'AVAILABLE'
    );
    """)

    self.conn.commit()

  def create_rental_table(self):
    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS Rentals (
    rental_id INTEGER PRIMARY KEY,
    house_id INTEGER NOT NULL,
    renter_name TEXT NOT NULL,
    contact_num TEXT NOT NULL,
    date_rented TEXT NOT NULL,
    duration_months INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    closed_date TEXT,
    cancel_reason TEXT,
    
    FOREIGN KEY (house_id)
    REFERENCES Houses(house_id)
    );
    """)

    self.conn.commit()

  def create_user(self, email, password):
    self.cursor.execute("""
    INSERT INTO Users (email, password)
    VALUES (?, ?);
    """, (email, password))

    self.conn.commit()

  def insert_house(self, owner, house, house_address, rent, bedrooms, bathrooms, house_type, date_added):
    cursor = self.cursor.execute("""
    INSERT INTO Houses (owner_name, house_name, house_address, monthly_rent, bedrooms, bathrooms, house_type, date_added
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (owner, house, house_address, rent, bedrooms, bathrooms, house_type, date_added))

    self.conn.commit()
    
    return cursor.lastrowid

  def insert_rental(self, house_id, renter_name, contact_num, date_rented, duration_months):
    self.cursor.execute("""
    INSERT INTO Rentals (house_id, renter_name, contact_num, date_rented, duration_months)
    VALUES (?, ?, ?, ?, ?);
    """, (house_id, renter_name, contact_num, date_rented, duration_months))

    self.conn.commit()

  def get_user_by_email(self, email):
    self.cursor.execute("""
    SELECT * FROM Users
    WHERE email = ?;
    """, (email,))

    return self.cursor.fetchone()

  def show_houses(self):
    self.cursor.execute("""
    SELECT * FROM Houses
    WHERE availability = 'AVAILABLE'
    ORDER BY house_id ASC;
    """)

    return self.cursor.fetchall()
    
  def show_house(self, house_id):
    self.cursor.execute("""
    SELECT * FROM Houses
    WHERE house_id = ?;
    """, (house_id,))
    
    return self.cursor.fetchone()
    
  def search_houses(self, location=None, house_type=None, min_bedrooms=None, min_bathrooms=None, max_monthly_rent=None):
    query = """
    SELECT * FROM Houses
    WHERE availability = 'AVAILABLE'
    """
    params = []
    
    if location:
      query += " AND house_address LIKE ?"
      params.append(f"%{location}%")
      
    if house_type:
      query += " AND house_type = ?"
      params.append(house_type)
      
    if min_bedrooms is not None:
      query += " AND bedrooms >= ?"
      params.append(min_bedrooms)
      
    if min_bathrooms is not None:
      query += " AND bathrooms >= ?"
      params.append(min_bathrooms)
      
    if max_monthly_rent is not None:
      query += " AND monthly_rent <= ?"
      params.append(max_monthly_rent)
    query += " ORDER BY house_id ASC;"
      
    self.cursor.execute(query, params)
    
    return self.cursor.fetchall()

  def show_rentals(self):
    self.cursor.execute("""
    SELECT * FROM Rentals
    ORDER BY rental_id ASC;
    """)

    return self.cursor.fetchall()
    
  def get_house_by_id(self, house_id):
    return self.cursor.execute("""
    SELECT * FROM Houses
    WHERE house_id = ?;
    """, (house_id,)).fetchone()
    
  def get_rental_by_id(self, rental_id):
    return self.cursor.execute("""
    SELECT * FROM Rentals
    WHERE rental_id = ?;
    """, (rental_id,)).fetchone()

  def rent_house_status(self, house_id):
    self.cursor.execute("""
    UPDATE Houses SET availability = 'RENTED'
    WHERE house_id = ?;
    """, (house_id,))

    self.conn.commit()
    
  def avail_house_status(self, house_id):
    self.cursor.execute("""
    UPDATE Houses SET availability = 'AVAILABLE'
    WHERE house_id = ?
    """, (house_id,))
    
    self.conn.commit()
    
  def not_avail_house_status(self, house_id):
    self.cursor.execute("""
    UPDATE Houses SET availability = 'NOT AVAILABLE'
    WHERE house_id = ?
    """, (house_id,))
    
    self.conn.commit()

  def update_rental_status(self, rental_id, closed_date, action, cancel_reason):
    self.cursor.execute("""
    UPDATE Rentals SET closed_date = ?, status = ?, cancel_reason = ?
    WHERE rental_id = ?
    """, (closed_date, action, cancel_reason, rental_id))
    
    self.conn.commit()
    
  def update_house(self, house_id, owner=None, house_name=None, house_address=None, monthly_rent=None, bedrooms=None, bathrooms=None, house_type=None):
    query = """
    UPDATE Houses SET
    """
    
    fields = []
    params = []
    
    if owner:
      fields.append("owner_name = ?")
      params.append(owner)
    
    if house_name:
      fields.append("house_name = ?")
      params.append(house_name)
      
    if house_address:
      fields.append("house_address = ?")
      params.append(house_address)
      
    if monthly_rent is not None:
      fields.append("monthly_rent = ?")
      params.append(monthly_rent)
      
    if bedrooms is not None:
      fields.append("bedrooms = ?")
      params.append(bedrooms)
      
    if bathrooms is not None:
      fields.append("bathrooms = ?")
      params.append(bathrooms)
      
    if house_type:
      fields.append("house_type = ?")
      params.append(house_type)
      
    if not fields:
      return
      
    query += ", ".join(fields)
    query += """
    WHERE house_id = ? 
    AND availability = 'AVAILABLE';
    """
    
    params.append(house_id)
    
    self.cursor.execute(query, params)
    
    self.conn.commit()
    
  def remove_house(self, house_id):
    rental_history = self.cursor.execute("""
    SELECT * FROM Rentals
    WHERE house_id = ?;
    """, (house_id,)).fetchone()
    
    if rental_history:
      return
    else:
      self.cursor.execute("""
      DELETE FROM Houses
      WHERE house_id = ? AND availability = 'AVAILABLE'
      """, (house_id,))
    
      self.conn.commit()