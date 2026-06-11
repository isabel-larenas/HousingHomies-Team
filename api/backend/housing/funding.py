from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

funding_bp = Blueprint("funding", __name__)

# Variable name includes the domain (ngo_bp) so it stays readable when
# imported alongside other blueprints (e.g. `from ... import ngo_bp, donor_bp`).


# Funding routes
# Read Funding
@funding_bp.route("/funding", methods=["GET"])
def get_funding():
    current_app.logger.info('GET /housing/funding')
    try:
        query = "SELECT * FROM funding JOIN country ON funding.country_id = country.country_id WHERE 1=1 "
        params = []
        
        country = request.args.get("country")
        year = request.args.get("year")
        amount = request.args.get("amount")
        program = request.args.get("program")
        agency = request.args.get("agency")
        
        if country:
            query += " AND country.country_name = %s"
            params.append(country)
        if year:
            query += " AND year = %s"
            params.append(year)
        if amount:
            query += " AND amount = %s"
            params.append(amount)
        if program:
            query += " AND program = %s"
            params.append(program)
        if agency:
            query += " AND agency = %s"
            params.append(agency)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            funding_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(funding_list)} funding records')
        return jsonify(funding_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_funding: {e}')
        return error_response(str(e))

#Create a new funding record
@funding_bp.route("/funding", methods=["POST"])
def create_funding():
    current_app.logger.info('POST /housing/funding')
    try:
        data = request.get_json()

        required_fields = ["funding_id", "country_id", "amount", "program", "agency"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        query = """
            INSERT INTO funding (funding_id, country_id, amount, program, agency)
            VALUES (%s, %s, %s, %s, %s)
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (
                data["funding_id"],
                data["country_id"],
                data["amount"],
                data["program"],
                data["agency"]
            ))
            new_id = cursor.lastrowid

        get_db().commit()
        current_app.logger.info(f'Created funding record with id={new_id}')
        return jsonify({"message": "Funding plan created successfully", "funding_id": new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_funding: {e}')
        return error_response(str(e))


# Update an existing funding record
# Can update any field except funding_id
# Example: PUT /housing/funding/1 with JSON body containing fields to update
@funding_bp.route("/funding/<int:funding_id>", methods=["PUT"])
def update_funding(funding_id):
    current_app.logger.info(f'PUT /funding/{funding_id}')
    try:
        data = request.get_json()

        # Build update query dynamically based on provided fields
        allowed_fields = ["amount", "program", "agency"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return error_response("No valid fields to update", 400)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT funding_id FROM funding WHERE funding_id = %s", (funding_id))
            if not cursor.fetchone():
                return error_response("Funding record not found", 404)

            params.append(funding_id)
            query = f"UPDATE funding SET {', '.join(update_fields)} WHERE funding_id = %s"
            cursor.execute(query, params)

        get_db().commit()
        return jsonify({"message": "Funding record updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_funding: {e}')
        return error_response(str(e))

# Delete a funding record
# Example: DELETE /housing/funding/1
@funding_bp.route("/funding/<int:funding_id>", methods=["DELETE"])
def delete_funding(funding_id):
    current_app.logger.info(f'DELETE /funding/{funding_id}')
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT funding_id FROM funding WHERE funding_id = %s", (funding_id))
            if not cursor.fetchone():
                return error_response("Funding record not found", 404)

            cursor.execute("DELETE FROM funding WHERE funding_id = %s", (funding_id,))

        get_db().commit()
        current_app.logger.info(f'Deleted funding id={funding_id}')
        return jsonify({"message": "Funding record deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_funding: {e}')
        return error_response(str(e))



@funding_bp.route("/funding-draft", methods=["POST"])
def create_funding_draft():
    current_app.logger.info('POST /funding-draft')
    try:
        data = request.get_json()

        with get_db().cursor() as cursor:
            cursor.execute("""
                INSERT INTO funding_draft (user_id, country_id, program, amount, indicators_targeted, demographics_targeted, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("user_id"),
                data.get("country_id"),
                data.get("program"),
                data.get("amount"),
                data.get("indicators_targeted"),
                data.get("demographics_targeted"),
                data.get("description")
            ))
        get_db().commit()
        return jsonify({"message": "Draft saved successfully"}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_funding_draft: {e}')
        return error_response(str(e))


@funding_bp.route("/funding-draft", methods=["GET"])
def get_funding_drafts():
    current_app.logger.info('GET /funding-draft')
    try:
        user_id = request.args.get("user_id")
        query = """
            SELECT fd.*, c.country_name 
            FROM funding_draft fd
            JOIN country c ON fd.country_id = c.country_id
            WHERE 1=1
        """
        params = []
        if user_id:
            query += " AND fd.user_id = %s"
            params.append(user_id)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            drafts = cursor.fetchall()

        return jsonify(drafts), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_funding_drafts: {e}')
        return error_response(str(e))
    

@funding_bp.route("/funding-draft/<int:draft_id>", methods = ["PUT"])
def update_funding_draft(draft_id):
    current_app.logger.info(f'PUT /funding-draft/{draft_id}')
    try:
        data = request.get_json()
        allowed = ["program", "amount", "indicators_targeted", "demographics_targeted", "description", "country_id"]
        update_fields = [f"{f} = %s" for f in allowed if f in data]
        params = [data[f] for f in allowed if f in data]

        if not update_fields:
            return error_response("No valid fields to update", 400)

        params.append(draft_id)
        with get_db().cursor() as cursor:
            cursor.execute(f"UPDATE funding_draft SET {', '.join(update_fields)} WHERE draft_id = %s", params)
        get_db().commit()
        return jsonify({"message": "Draft updated"}), 200
    except Error as e:
        return error_response(str(e))


@funding_bp.route("/funding-draft/<int:draft_id>", methods = ["DELETE"])
def delete_funding_draft(draft_id):
    current_app.logger.info(f'DELETE /funding-draft/{draft_id}')
    try:
        with get_db().cursor() as cursor:
            cursor.execute("DELETE FROM funding_draft WHERE draft_id = %s", (draft_id,))
        get_db().commit()
        return jsonify({"message": "Draft deleted"}), 200
    except Error as e:
        return error_response(str(e))