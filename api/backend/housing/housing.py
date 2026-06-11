from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error
import requests

# Variable name includes the domain (ngo_bp) so it stays readable when
# imported alongside other blueprints (e.g. `from ... import ngo_bp, donor_bp`).
housing_bp = Blueprint("housing", __name__)

# --- country -------------------------------
@housing_bp.route("/country", methods=["GET"])
def get_country():
    current_app.logger.info('GET /housing/country')
    try:
        query = "SELECT * FROM country WHERE 1=1 "
        params = []
        
        country = request.args.get("country")
        if country:
            query += " AND Country = %s"
            params.append(country)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            country_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(country_list)} countries')
        return jsonify(country_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_countries: {e}')
        return error_response(str(e))


#User routes
@housing_bp.route("/user", methods=["GET"])
def get_user():
    current_app.logger.info('GET /housing/user')
    try:
        query = "SELECT * FROM user JOIN country on user.country_id = country.country_id WHERE 1=1 "
        params = []
       
        name = request.args.get("name")
        country = request.args.get("country")
        role = request.args.get("role")
        if name:
            query += " AND name = %s"
            params.append(name)
        if country:
            query += " AND country.country_name = %s"
            params.append(country)
        if role:
            query += " AND role = %s"
            params.append(role)




        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            user_list = cursor.fetchall()


        current_app.logger.info(f'Retrieved {len(user_list)} users')
        return jsonify(user_list), 200
    
    except Error as e:
        current_app.logger.error(f'Database error in get_all_users: {e}')
        return error_response(str(e))

#Update user
@housing_bp.route("/housing/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    current_app.logger.info(f'PUT /housing/user/{user_id}')
    try:
        data = request.get_json()


        #which fields can be updated
        allowed_fields = ["university", "country", "email", "max_budget"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]


        if not update_fields:
            return error_response("No valid fields to update", 400)


        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT user_id FROM user WHERE user_id = %s", (user_id))
            if not cursor.fetchone():
                return error_response("User not found", 404)


            params.append(user_id)
            query = f"UPDATE user SET {', '.join(update_fields)} WHERE user_id = %s"
            cursor.execute(query, params)


        get_db().commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_user: {e}')
        return error_response(str(e))


#Get unviersity
@housing_bp.route("/university", methods=["GET"])
def get_university():
    current_app.logger.info('GET /housing/university')
    try:
        query = query = """SELECT DISTINCT university.*, country.country_name 
        FROM university 
        JOIN country ON university.country_id = country.country_id
        LEFT JOIN listing ON listing.associated_university_id = university.university_id
        WHERE 1=1"""
        params = []

        name = request.args.get("university_name")
        country = request.args.get("country_name")
        city_name = request.args.get("city_name")
        listing_id = request.args.get("listing_id")

        if name:
            query += " AND university.university_name = %s"
            params.append(name)
        if country:
            query += " AND country.country_name = %s"
            params.append(country)
        if city_name:
            query += " AND university.city_name = %s"
            params.append(city_name)
        if listing_id:
            query += " AND listing.listing_id = %s"
            params.append(listing_id)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            university_list = cursor.fetchall()


        current_app.logger.info(f'Retrieved {len(university_list)} universities')
        return jsonify(university_list), 200

    except Error as e:
        current_app.logger.error(f'Database error in get_university: {e}')
        return error_response(str(e))

#get cities
@housing_bp.route("/listing/cities", methods=["GET"])
def get_cities():
    current_app.logger.info('GET /housing/listing/cities')
    try:
        query = """
            SELECT DISTINCT listing.city_name
            FROM listing
            ORDER BY listing.city_name ASC
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query)
            cities = cursor.fetchall()

        return jsonify(cities), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_cities: {e}')
        return error_response(str(e))


