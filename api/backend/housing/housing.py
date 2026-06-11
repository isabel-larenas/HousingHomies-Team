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


# # --- social indicator types -------------------------------
# @housing_bp.route("/social-indicator-types", methods=["GET"])
# def get_all_social_indicator_types():
#     current_app.logger.info('GET /housing/social-indicator-types')
#     try:
#         query = "SELECT * FROM social_indicator_types WHERE 1=1"
#         params = []

#         name = request.args.get("name")
#         if name:
#             query += " AND name = %s"
#             params.append(name)

#         with get_db().cursor(dictionary=True) as cursor:
#             cursor.execute(query, params)
#             social_indicator_types_list = cursor.fetchall()

#         current_app.logger.info(f'Retrieved {len(social_indicator_types_list)} social indicator types')
#         return jsonify(social_indicator_types_list), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_all_social_indicator_types: {e}')
#         return error_response(str(e))


# @housing_bp.route("/social-indicator-stats", methods=["GET"])
# def get_social_indicator_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats')
#     try:
#         country = request.args.get("country")
#         year = request.args.get("year")
#         type = request.args.get("social_indicator_type")

#         query = "SELECT * FROM social_indicator_stats " \
#         "JOIN social_indicator_types ON social_indicator_stats.sit_id = social_indicator_types.sit_id " \
#         "JOIN country ON social_indicator_stats.country_id = country.country_id " \
#         "WHERE 1=1"
#         params = []

#         if country:
#             query += " AND country.country_name = %s"
#             params.append(country)
#         if year:
#             query += " AND year = %s"
#             params.append(year)
#         if type:
#             query += " AND social_indicator_types.name = %s"
#             params.append(type)

#         with get_db().cursor(dictionary=True) as cursor:
#             cursor.execute(query, params)
#             stats = cursor.fetchall()

#         return jsonify(stats), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_social_indicator_stats: {e}')
#         return error_response(str(e))



# def sync_eurostat(url, sit_id):
#     response = requests.get(url, params={"format": "JSON", "lang": "EN"})
#     data = response.json()

#     values = data["value"]
#     dim_ids = data["id"]
#     dimensions = data["dimension"]
#     dim_sizes = [len(dimensions[d]["category"]["index"]) for d in dim_ids]

#     countries = dimensions["geo"]["category"]["index"]
#     years = dimensions["time"]["category"]["index"]
#     geo_pos = dim_ids.index("geo")
#     time_pos = dim_ids.index("time")

#     rows = []
#     for country_code, country_idx in countries.items():
#         for year, year_idx in years.items():
#             indices = [0] * len(dim_ids)
#             indices[geo_pos] = country_idx
#             indices[time_pos] = year_idx

#             key = 0
#             multiplier = 1
#             for i in range(len(dim_ids) - 1, -1, -1):
#                 key += indices[i] * multiplier
#                 multiplier *= dim_sizes[i]

#             value = values.get(str(key))
#             if value is not None:
#                 rows.append((sit_id, year, value, country_code))

#     db = get_db()
#     with db.cursor() as cursor:
#         cursor.execute("DELETE FROM social_indicator_stats WHERE sit_id = %s", (sit_id,))
#     db.commit()

#     with db.cursor() as cursor:
#         cursor.executemany("""
#             INSERT INTO social_indicator_stats (country_id, sit_id, year, value)
#             SELECT c.country_id, %s, %s, %s
#             FROM country c
#             WHERE c.country_code = %s
#         """, rows)
#     db.commit()

#     return len(rows)

# def get_stats_by_sit_id(sit_id):
#     country = request.args.get("country")
#     year = request.args.get("year")

#     query = """
#         SELECT sis.stats_id, c.country_name, c.country_code, sis.year, sis.value
#         FROM social_indicator_stats sis
#         JOIN country c ON sis.country_id = c.country_id
#         WHERE sis.sit_id = %s
#     """
#     params = [sit_id]

#     if country:
#         query += " AND c.country_name = %s"
#         params.append(country)
#     if year:
#         query += " AND sis.year = %s"
#         params.append(year)

#     with get_db().cursor(dictionary=True) as cursor:
#         cursor.execute(query, params)
#         return cursor.fetchall()
    

# # --- Pollution (sit_id = 1) -------------------------------
# @housing_bp.route("/social-indicator-stats/pollution", methods=["POST"])
# def sync_pollution():
#     current_app.logger.info('POST /housing/social-indicator-stats/pollution')
#     try:
#         count = sync_eurostat(
#             "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mddw05",
#             sit_id=1
#         )
#         return jsonify({"message": f"Synced {count} pollution records"}), 201
#     except Exception as e:
#         current_app.logger.error(f'Error syncing pollution data: {e}')
#         return error_response(str(e))


# @housing_bp.route("/social-indicator-stats/pollution", methods=["GET"])
# def get_pollution_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats/pollution')
#     try:
#         return jsonify(get_stats_by_sit_id(1)), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_pollution_stats: {e}')
#         return error_response(str(e))

# # --- Crime (sit_id = 2) -------------------------------

# @housing_bp.route("/social-indicator-stats/crime", methods=["POST"])
# def sync_crime():
#     current_app.logger.info('POST /housing/social-indicator-stats/crime')
#     try:
#         count = sync_eurostat(
#             "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mddw03",
#             sit_id=2
#         )
#         return jsonify({"message": f"Synced {count} crime records"}), 201
#     except Exception as e:
#         current_app.logger.error(f'Error syncing crime data: {e}')
#         return error_response(str(e))


# @housing_bp.route("/social-indicator-stats/crime", methods=["GET"])
# def get_crime_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats/crime')
#     try:
#         return jsonify(get_stats_by_sit_id(2)), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_crime_stats: {e}')
#         return error_response(str(e))


# # --- Poverty (sit_id = 3) -------------------------------

# @housing_bp.route("/social-indicator-stats/poverty", methods=["POST"])
# def sync_poverty():
#     current_app.logger.info('POST /housing/social-indicator-stats/poverty')
#     try:
#         count = sync_eurostat(
#             "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07a",
#             sit_id=3
#         )
#         return jsonify({"message": f"Synced {count} poverty records"}), 201
#     except Exception as e:
#         current_app.logger.error(f'Error syncing poverty data: {e}')
#         return error_response(str(e))


# @housing_bp.route("/social-indicator-stats/poverty", methods=["GET"])
# def get_poverty_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats/poverty')
#     try:
#         return jsonify(get_stats_by_sit_id(3)), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_poverty_stats: {e}')
#         return error_response(str(e))


# # --- Overcrowding (sit_id = 4) -----------------------------
# @housing_bp.route("/social-indicator-stats/overcrowding", methods=["POST"])
# def sync_overcrowding():
#     current_app.logger.info('POST /housing/social-indicator-stats/overcrowding')
#     try:
#         count = sync_eurostat(
#             "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07b",
#             sit_id=4
#         )
#         return jsonify({"message": f"Synced {count} overcrowding records"}), 201
#     except Exception as e:
#         current_app.logger.error(f'Error syncing overcrowding data: {e}')
#         return error_response(str(e))
    

# @housing_bp.route("/social-indicator-stats/overcrowding", methods=["GET"])
# def get_overcrowding_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats/overcrowding')
#     try:
#         return jsonify(get_stats_by_sit_id(4)), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_overcrowding_stats: {e}')
#         return error_response(str(e))

# # --- Noise (sit_id = 5) -------------------------------

# @housing_bp.route("/social-indicator-stats/noise", methods=["POST"])
# def sync_noise():
#     current_app.logger.info('POST /housing/social-indicator-stats/noise')
#     try:
#         count = sync_eurostat(
#             "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mddw04?deg_urb=DEG1&rskpovth=TOTAL",
#             sit_id=5
#         )
#         return jsonify({"message": f"Synced {count} noise records"}), 201
#     except Exception as e:
#         current_app.logger.error(f'Error syncing noise data: {e}')
#         return error_response(str(e))


# @housing_bp.route("/social-indicator-stats/noise", methods=["GET"])
# def get_noise_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats/noise')
#     try:
#         return jsonify(get_stats_by_sit_id(5)), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_noise_stats: {e}')
#         return error_response(str(e))

# # --- House Price Index (sit_id = 6) -------------------------------
# @housing_bp.route("/social-indicator-stats/hpi", methods=["POST"])
# def sync_hpi():
#     current_app.logger.info('POST /housing/social-indicator-stats/hpi')
#     try:
#         count = sync_eurostat(
#             "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hpi_a?purchase=TOTAL&unit=I15_A_AVG",
#             sit_id=6
#         )
#         return jsonify({"message": f"Synced {count} HPI records"}), 201
#     except Exception as e:
#         current_app.logger.error(f'Error syncing HPI data: {e}')
#         return error_response(str(e))

# @housing_bp.route("/social-indicator-stats/hpi", methods=["GET"])
# def get_hpi_stats():
#     current_app.logger.info('GET /housing/social-indicator-stats/hpi')
#     try:
#         return jsonify(get_stats_by_sit_id(6)), 200
#     except Error as e:
#         current_app.logger.error(f'Database error in get_hpi_stats: {e}')
#         return error_response(str(e))
    

# # ML model routes for student
# # train model
# @housing_bp.route("/student/train", methods=["POST"])
# def train_model():
#     current_app.logger.info('POST /student/train')
#     try:
#         results = train()
#         return jsonify({
#             "message": "Model trained successfully",
#             "mse": results["mse"],
#             "r2":  results["r2"]
#         }), 201
#     except Exception as e:
#         current_app.logger.error(f'Error training student model: {e}')
#         return error_response(str(e))
 
 
# # test model
# @housing_bp.route("/student/test", methods=["GET"])
# def test_model():
#     current_app.logger.info('GET /student/test')
#     try:
#         results = test()
#         return jsonify({
#             "mse": results["mse"],
#             "r2":  results["r2"]
#         }), 200
#     except ValueError as e:
#         current_app.logger.error(f'No model parameters found: {e}')
#         return error_response(str(e), 404)
#     except Exception as e:
#         current_app.logger.error(f'Error testing student model: {e}')
#         return error_response(str(e))
 
 
# # predict
# @housing_bp.route("/student/predict", methods=["POST"])
# def predict_satisfaction():
#     current_app.logger.info('POST /student/predict')
#     try:
#         data = request.get_json()

#         required = ["crime", "noise", "pollution", "hpi", "is_rural", "is_towns"]
#         missing = [f for f in required if f not in data]
#         if missing:
#             return error_response(f"Missing required fields: {missing}", 400)

#         score, all_countries = predict(
#             crime      = float(data["crime"]),
#             noise      = float(data["noise"]),
#             pollution  = float(data["pollution"]),
#             hpi        = float(data["hpi"]),
#             is_rural   = bool(data["is_rural"]),
#             is_towns   = bool(data["is_towns"]),
#         )

#         return jsonify({"prediction": round(score, 2), "all_countries": all_countries}), 200

#     except ValueError as e:
#         current_app.logger.error(f'No model parameters found: {e}')
#         return error_response(str(e), 404)
#     except Exception as e:
#         current_app.logger.error(f'Error in predict_satisfaction: {e}')
#         return error_response(str(e))
 
 
# # stored model params
# @housing_bp.route("/student/params", methods=["GET"])
# def get_model_params():
#     current_app.logger.info('GET /student/params')
#     try:
#         with get_db().cursor(dictionary=True) as cursor:
#             cursor.execute(
#                 '''SELECT id, beta_vals, scaler_mean, scaler_std
#                    FROM student_model_params
#                    ORDER BY id DESC LIMIT 1'''
#             )
#             row = cursor.fetchone()
 
#         if row is None:
#             return error_response("No model parameters found. Run train first.", 404)
 
#         return jsonify(row), 200
 
#     except Error as e:
#         current_app.logger.error(f'Database error in get_model_params: {e}')
#         return error_response(str(e))
    
# # ML model routes for government agency
# # train model
# @housing_bp.route("/government/train", methods=["POST"])
# def government_train_model():
#     current_app.logger.info('POST /government/train')
#     try:
#         results = gov_train()
#         return jsonify({
#             "message": "Model trained successfully",
#             "mse": results["mse"],
#             "r2":  results["r2"]
#         }), 201
#     except Exception as e:
#         current_app.logger.error(f'Error training government model: {e}')
#         return error_response(str(e))
 
 
# # test model
# @housing_bp.route("/government/test", methods=["GET"])
# def government_test_model():
#     current_app.logger.info('GET /government/test')
#     try:
#         results = gov_test()
#         return jsonify({
#             "mse": results["mse"],
#             "r2":  results["r2"]
#         }), 200
#     except ValueError as e:
#         current_app.logger.error(f'No model parameters found: {e}')
#         return error_response(str(e), 404)
#     except Exception as e:
#         current_app.logger.error(f'Error testing government model: {e}')
#         return error_response(str(e))
 
 
# # predict
# @housing_bp.route("/government/predict", methods=["POST"])
# def predict_housing_deprivation():
#     current_app.logger.info('POST /government/predict')
#     try:
#         data = request.get_json()
 
#         required = ["immigration_count", "overburden_rate", "gdp_per_capita", "population_density", "unemployment_rate"]
#         missing = [f for f in required if f not in data]
#         if missing:
#             return error_response(f"Missing required fields: {missing}", 400)
 
#         score = gov_predict(
#             immigration_count = float(data["immigration_count"]),
#             overburden_rate = float(data["overburden_rate"]),
#             gdp_per_capita = float(data["gdp_per_capita"]),
#             population_density = float(data["population_density"]),
#             unemployment_rate = float(data["unemployment_rate"]),
#         )

#         return jsonify({"prediction": round(score, 2)}), 200
 
#     except ValueError as e:
#         current_app.logger.error(f'No model parameters found: {e}')
#         return error_response(str(e), 404)
#     except Exception as e:
#         current_app.logger.error(f'Error in predict_housing_deprivation: {e}')
#         return error_response(str(e))
 
 
# # per-country predicted deprivation, for the Europe heatmap
# @housing_bp.route("/government/deprivation-map", methods=["GET"])
# def government_deprivation_map():
#     current_app.logger.info('GET /government/deprivation-map')
#     try:
#         return jsonify(gov_predict_all()), 200
#     except ValueError as e:
#         current_app.logger.error(f'No model parameters found: {e}')
#         return error_response(str(e), 404)
#     except Exception as e:
#         current_app.logger.error(f'Error in government_deprivation_map: {e}')
#         return error_response(str(e))


# # stored model params
# @housing_bp.route("/government/params", methods=["GET"])
# def government_get_model_params():
#     current_app.logger.info('GET /government/params')
#     try:
#         with get_db().cursor(dictionary=True) as cursor:
#             cursor.execute(
#                 '''SELECT id, ga_beta_vals, ga_scaler_mean, ga_scaler_std
#                    FROM gov_model_params
#                    ORDER BY id DESC LIMIT 1'''
#             )
#             row = cursor.fetchone()
 
#         if row is None:
#             return error_response("No model parameters found. Run train first.", 404)
 
#         return jsonify(row), 200
 
#     except Error as e:
#         current_app.logger.error(f'Database error in government_get_model_params: {e}')
#         return error_response(str(e))

