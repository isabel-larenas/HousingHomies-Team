from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from backend.utils import error_response
from mysql.connector import Error
from backend.ml_models.student_linreg import train, test, predict
from backend.ml_models.government_linreg import (
    train as gov_train,
    test as gov_test,
    predict as gov_predict,
    predict_all_countries as gov_predict_all,
)

prediction_bp = Blueprint("prediction", __name__)

# ML model routes for student
# train model
@prediction_bp.route("/student/train", methods=["POST"])
def train_model():
    current_app.logger.info('POST /student/train')
    try:
        results = train()
        return jsonify({
            "message": "Model trained successfully",
            "mse": results["mse"],
            "r2":  results["r2"]
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error training student model: {e}')
        return error_response(str(e))
 
 
# test model
@prediction_bp.route("/student/test", methods=["GET"])
def test_model():
    current_app.logger.info('GET /student/test')
    try:
        results = test()
        return jsonify({
            "mse": results["mse"],
            "r2":  results["r2"]
        }), 200
    except ValueError as e:
        current_app.logger.error(f'No model parameters found: {e}')
        return error_response(str(e), 404)
    except Exception as e:
        current_app.logger.error(f'Error testing student model: {e}')
        return error_response(str(e))
 
 
# predict
@prediction_bp.route("/student/prediction", methods=["POST"])
def predict_satisfaction():
    current_app.logger.info('POST /student/prediction')
    try:
        data = request.get_json()

        required = ["crime", "noise", "pollution", "hpi", "is_rural", "is_towns"]
        missing = [f for f in required if f not in data]
        if missing:
            return error_response(f"Missing required fields: {missing}", 400)

        score, all_countries = predict(
            crime      = float(data["crime"]),
            noise      = float(data["noise"]),
            pollution  = float(data["pollution"]),
            hpi        = float(data["hpi"]),
            is_rural   = bool(data["is_rural"]),
            is_towns   = bool(data["is_towns"]),
        )

        return jsonify({"prediction": round(score, 2), "all_countries": all_countries}), 200

    except ValueError as e:
        current_app.logger.error(f'No model parameters found: {e}')
        return error_response(str(e), 404)
    except Exception as e:
        current_app.logger.error(f'Error in predict_satisfaction: {e}')
        return error_response(str(e))
 
 
# stored model params
@prediction_bp.route("/student/params", methods=["GET"])
def get_model_params():
    current_app.logger.info('GET /student/params')
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                '''SELECT id, beta_vals, scaler_mean, scaler_std
                   FROM student_model_params
                   ORDER BY id DESC LIMIT 1'''
            )
            row = cursor.fetchone()
 
        if row is None:
            return error_response("No model parameters found. Run train first.", 404)
 
        return jsonify(row), 200
 
    except Error as e:
        current_app.logger.error(f'Database error in get_model_params: {e}')
        return error_response(str(e))
    
# ML model routes for government agency
# train model
@prediction_bp.route("/government/train", methods=["POST"])
def government_train_model():
    current_app.logger.info('POST /government/train')
    try:
        results = gov_train()
        return jsonify({
            "message": "Model trained successfully",
            "mse": results["mse"],
            "r2":  results["r2"]
        }), 201
    except Exception as e:
        current_app.logger.error(f'Error training government model: {e}')
        return error_response(str(e))
 
 
# test model
@prediction_bp.route("/government/test", methods=["GET"])
def government_test_model():
    current_app.logger.info('GET /government/test')
    try:
        results = gov_test()
        return jsonify({
            "mse": results["mse"],
            "r2":  results["r2"]
        }), 200
    except ValueError as e:
        current_app.logger.error(f'No model parameters found: {e}')
        return error_response(str(e), 404)
    except Exception as e:
        current_app.logger.error(f'Error testing government model: {e}')
        return error_response(str(e))
 
 
# predict
@prediction_bp.route("/government/prediction", methods=["POST"])
def predict_housing_deprivation():
    current_app.logger.info('POST /government/prediction')
    try:
        data = request.get_json()
 
        required = ["immigration_count", "overburden_rate", "gdp_per_capita", "population_density", "unemployment_rate"]
        missing = [f for f in required if f not in data]
        if missing:
            return error_response(f"Missing required fields: {missing}", 400)
 
        score = gov_predict(
            immigration_count = float(data["immigration_count"]),
            overburden_rate = float(data["overburden_rate"]),
            gdp_per_capita = float(data["gdp_per_capita"]),
            population_density = float(data["population_density"]),
            unemployment_rate = float(data["unemployment_rate"]),
        )

        return jsonify({"prediction": round(score, 2)}), 200
 
    except ValueError as e:
        current_app.logger.error(f'No model parameters found: {e}')
        return error_response(str(e), 404)
    except Exception as e:
        current_app.logger.error(f'Error in predict_housing_deprivation: {e}')
        return error_response(str(e))
 
 
# per-country predicted deprivation, for the Europe heatmap
@prediction_bp.route("/government/deprivation-map", methods=["GET"])
def government_deprivation_map():
    current_app.logger.info('GET /government/deprivation-map')
    try:
        return jsonify(gov_predict_all()), 200
    except ValueError as e:
        current_app.logger.error(f'No model parameters found: {e}')
        return error_response(str(e), 404)
    except Exception as e:
        current_app.logger.error(f'Error in government_deprivation_map: {e}')
        return error_response(str(e))


# stored model params
@prediction_bp.route("/government/params", methods=["GET"])
def government_get_model_params():
    current_app.logger.info('GET /government/params')
    try:
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                '''SELECT id, ga_beta_vals, ga_scaler_mean, ga_scaler_std
                   FROM gov_model_params
                   ORDER BY id DESC LIMIT 1'''
            )
            row = cursor.fetchone()
 
        if row is None:
            return error_response("No model parameters found. Run train first.", 404)
 
        return jsonify(row), 200
 
    except Error as e:
        current_app.logger.error(f'Database error in government_get_model_params: {e}')
        return error_response(str(e))

