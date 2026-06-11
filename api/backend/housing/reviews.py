from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error

reviews_bp = Blueprint("reviews", __name__)

# Variable name includes the domain (ngo_bp) so it stays readable when
# imported alongside other blueprints (e.g. `from ... import ngo_bp, donor_bp`).

# Reviews routes
# Read review
@reviews_bp.route("/reviews", methods=["GET"])
def get_reviews():
    current_app.logger.info('GET /housing/reviews')
    try:
        query = "SELECT * FROM reviews WHERE 1=1 "
        params = []
        
        listing_id = request.args.get("listing_id")
        rating = request.args.get("rating")
        if listing_id:
            query += " AND listing_id = %s"
            params.append(listing_id)
        if rating:
            query += " AND rating = %s"
            params.append(rating)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            reviews_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(reviews_list)} reviews')
        return jsonify(reviews_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_reviews: {e}')
        return error_response(str(e))
    
#Create a new review
@reviews_bp.route("/reviews", methods=["POST"])
def create_review():
    current_app.logger.info('POST /housing/reviews')
    try:
        data = request.get_json()

        required_fields = ["listing_id", "rating", "comment"]
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        query = """
            INSERT INTO Reviews (listing_id, rating, comment)
            VALUES (%s, %s, %s)
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(query, (
                data["listing_id"],
                data.get("rating"),
                data["comment"]
            ))
            new_id = cursor.lastrowid

        get_db().commit()
        current_app.logger.info(f'Created review with id={new_id}')
        return jsonify({"message": "Review created successfully", "review_id": new_id}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_review: {e}')
        return error_response(str(e))


# Update an existing reviews's information
# Can update any field except review_id
# Example: PUT /housing/review/1 with JSON body containing fields to update
@reviews_bp.route("/review/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    current_app.logger.info(f'PUT /housing/review/{review_id}')
    try:
        data = request.get_json()

        # Build update query dynamically based on provided fields
        allowed_fields = ["rating", "comment"]
        update_fields = [f"{f} = %s" for f in allowed_fields if f in data]
        params = [data[f] for f in allowed_fields if f in data]

        if not update_fields:
            return error_response("No valid fields to update", 400)

        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT review_id FROM reviews WHERE review_id = %s", (review_id))
            if not cursor.fetchone():
                return error_response("Review not found", 404)

            params.append(review_id)
            query = f"UPDATE reviews SET {', '.join(update_fields)} WHERE review_id = %s"
            cursor.execute(query, params)

        get_db().commit()
        return jsonify({"message": "Review updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_review: {e}')
        return error_response(str(e))

# Delete a review
# Example: DELETE /housing/review/1
@reviews_bp.route("/review/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    current_app.logger.info(f'DELETE /housing/review/{review_id}')
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute("SELECT review_id FROM reviews WHERE review_id = %s", (review_id))
            if not cursor.fetchone():
                return error_response("Review not found", 404)

            cursor.execute("DELETE FROM reviews WHERE review_id = %s", (review_id))

        get_db().commit()
        current_app.logger.info(f'Deleted review id={review_id}')
        return jsonify({"message": "Review deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_review: {e}')
        return error_response(str(e))