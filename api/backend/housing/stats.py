from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error
import requests

stats_bp = Blueprint("stats", __name__)


# --- social indicator types -------------------------------
@stats_bp.route("/social-indicator-types", methods=["GET"])
def get_all_social_indicator_types():
    current_app.logger.info('GET /housing/social-indicator-types')
    try:
        query = "SELECT * FROM social_indicator_types WHERE 1=1"
        params = []

        name = request.args.get("name")
        if name:
            query += " AND name = %s"
            params.append(name)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            social_indicator_types_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(social_indicator_types_list)} social indicator types')
        return jsonify(social_indicator_types_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_social_indicator_types: {e}')
        return error_response(str(e))


@stats_bp.route("/social-indicator-stats", methods=["GET"])
def get_social_indicator_stats():
    current_app.logger.info('GET /stats/social-indicator-stats')
    try:
        country = request.args.get("country")
        year = request.args.get("year")
        type = request.args.get("social_indicator_type")

        query = "SELECT * FROM social_indicator_stats " \
        "JOIN social_indicator_types ON social_indicator_stats.sit_id = social_indicator_types.sit_id " \
        "JOIN country ON social_indicator_stats.country_id = country.country_id " \
        "WHERE 1=1"
        params = []

        if country:
            query += " AND country.country_name = %s"
            params.append(country)
        if year:
            query += " AND year = %s"
            params.append(year)
        if type:
            query += " AND social_indicator_types.name = %s"
            params.append(type)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            stats = cursor.fetchall()

        return jsonify(stats), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_social_indicator_stats: {e}')
        return error_response(str(e))



def sync_eurostat(url, sit_id):
    response = requests.get(url, params={"format": "JSON", "lang": "EN"})
    data = response.json()

    values = data["value"]
    dim_ids = data["id"]
    dimensions = data["dimension"]
    dim_sizes = [len(dimensions[d]["category"]["index"]) for d in dim_ids]

    countries = dimensions["geo"]["category"]["index"]
    years = dimensions["time"]["category"]["index"]
    geo_pos = dim_ids.index("geo")
    time_pos = dim_ids.index("time")

    rows = []
    for country_code, country_idx in countries.items():
        for year, year_idx in years.items():
            indices = [0] * len(dim_ids)
            indices[geo_pos] = country_idx
            indices[time_pos] = year_idx

            key = 0
            multiplier = 1
            for i in range(len(dim_ids) - 1, -1, -1):
                key += indices[i] * multiplier
                multiplier *= dim_sizes[i]

            value = values.get(str(key))
            if value is not None:
                rows.append((sit_id, year, value, country_code))

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM social_indicator_stats WHERE sit_id = %s", (sit_id,))
    db.commit()

    with db.cursor() as cursor:
        cursor.executemany("""
            INSERT INTO social_indicator_stats (country_id, sit_id, year, value)
            SELECT c.country_id, %s, %s, %s
            FROM country c
            WHERE c.country_code = %s
        """, rows)
    db.commit()

    return len(rows)

def get_stats_by_sit_id(sit_id):
    country = request.args.get("country")
    year = request.args.get("year")

    query = """
        SELECT sis.stats_id, c.country_name, c.country_code, sis.year, sis.value
        FROM social_indicator_stats sis
        JOIN country c ON sis.country_id = c.country_id
        WHERE sis.sit_id = %s
    """
    params = [sit_id]

    if country:
        query += " AND c.country_name = %s"
        params.append(country)
    if year:
        query += " AND sis.year = %s"
        params.append(year)

    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()
    

# --- Pollution (sit_id = 1) -------------------------------
@stats_bp.route("/social-indicator-stats/pollution", methods=["POST"])
def sync_pollution():
    current_app.logger.info('POST /stats/social-indicator-stats/pollution')
    try:
        count = sync_eurostat(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mddw05",
            sit_id=1
        )
        return jsonify({"message": f"Synced {count} pollution records"}), 201
    except Exception as e:
        current_app.logger.error(f'Error syncing pollution data: {e}')
        return error_response(str(e))


@stats_bp.route("/social-indicator-stats/pollution", methods=["GET"])
def get_pollution_stats():
    current_app.logger.info('GET /stats/social-indicator-stats/pollution')
    try:
        return jsonify(get_stats_by_sit_id(1)), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_pollution_stats: {e}')
        return error_response(str(e))

# --- Crime (sit_id = 2) -------------------------------

@stats_bp.route("/social-indicator-stats/crime", methods=["POST"])
def sync_crime():
    current_app.logger.info('POST /stats/social-indicator-stats/crime')
    try:
        count = sync_eurostat(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mddw03",
            sit_id=2
        )
        return jsonify({"message": f"Synced {count} crime records"}), 201
    except Exception as e:
        current_app.logger.error(f'Error syncing crime data: {e}')
        return error_response(str(e))


@stats_bp.route("/social-indicator-stats/crime", methods=["GET"])
def get_crime_stats():
    current_app.logger.info('GET /stats/social-indicator-stats/crime')
    try:
        return jsonify(get_stats_by_sit_id(2)), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_crime_stats: {e}')
        return error_response(str(e))


# --- Poverty (sit_id = 3) -------------------------------

@stats_bp.route("/social-indicator-stats/poverty", methods=["POST"])
def sync_poverty():
    current_app.logger.info('POST /stats/social-indicator-stats/poverty')
    try:
        count = sync_eurostat(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07a",
            sit_id=3
        )
        return jsonify({"message": f"Synced {count} poverty records"}), 201
    except Exception as e:
        current_app.logger.error(f'Error syncing poverty data: {e}')
        return error_response(str(e))


@stats_bp.route("/social-indicator-stats/poverty", methods=["GET"])
def get_poverty_stats():
    current_app.logger.info('GET /stats/social-indicator-stats/poverty')
    try:
        return jsonify(get_stats_by_sit_id(3)), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_poverty_stats: {e}')
        return error_response(str(e))


# --- Overcrowding (sit_id = 4) -----------------------------
@stats_bp.route("/social-indicator-stats/overcrowding", methods=["POST"])
def sync_overcrowding():
    current_app.logger.info('POST /stats/social-indicator-stats/overcrowding')
    try:
        count = sync_eurostat(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_lvho07b",
            sit_id=4
        )
        return jsonify({"message": f"Synced {count} overcrowding records"}), 201
    except Exception as e:
        current_app.logger.error(f'Error syncing overcrowding data: {e}')
        return error_response(str(e))
    

@stats_bp.route("/social-indicator-stats/overcrowding", methods=["GET"])
def get_overcrowding_stats():
    current_app.logger.info('GET /stats/social-indicator-stats/overcrowding')
    try:
        return jsonify(get_stats_by_sit_id(4)), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_overcrowding_stats: {e}')
        return error_response(str(e))

# --- Noise (sit_id = 5) -------------------------------

@stats_bp.route("/social-indicator-stats/noise", methods=["POST"])
def sync_noise():
    current_app.logger.info('POST /stats/social-indicator-stats/noise')
    try:
        count = sync_eurostat(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_mddw04?deg_urb=DEG1&rskpovth=TOTAL",
            sit_id=5
        )
        return jsonify({"message": f"Synced {count} noise records"}), 201
    except Exception as e:
        current_app.logger.error(f'Error syncing noise data: {e}')
        return error_response(str(e))


@stats_bp.route("/social-indicator-stats/noise", methods=["GET"])
def get_noise_stats():
    current_app.logger.info('GET /stats/social-indicator-stats/noise')
    try:
        return jsonify(get_stats_by_sit_id(5)), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_noise_stats: {e}')
        return error_response(str(e))

# --- House Price Index (sit_id = 6) -------------------------------
@stats_bp.route("/social-indicator-stats/hpi", methods=["POST"])
def sync_hpi():
    current_app.logger.info('POST /stats/social-indicator-stats/hpi')
    try:
        count = sync_eurostat(
            "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hpi_a?purchase=TOTAL&unit=I15_A_AVG",
            sit_id=6
        )
        return jsonify({"message": f"Synced {count} HPI records"}), 201
    except Exception as e:
        current_app.logger.error(f'Error syncing HPI data: {e}')
        return error_response(str(e))

@stats_bp.route("/social-indicator-stats/hpi", methods=["GET"])
def get_hpi_stats():
    current_app.logger.info('GET /stats/social-indicator-stats/hpi')
    try:
        return jsonify(get_stats_by_sit_id(6)), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_hpi_stats: {e}')
        return error_response(str(e))
    