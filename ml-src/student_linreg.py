import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from flask import current_app
from backend.db_connection import get_db
from sklearn.linear_model import LinearRegression

cols = [
    'crime_rate', 'noise_rate', 'pollution_rate', 'hpi_weight',
    'deg_urb_Rural areas', 'deg_urb_Towns and suburbs', 'crime_noise', 'poll_noise', 'crime_hpi', 'poll_crime'
]

import os
import backend.ml_models
# This module lives in ml-src/ (placed on PYTHONPATH so the backend can import
# it as a top-level module), but its training data lives with the backend
# package. Resolve the data dir from the backend.ml_models package location so
# the CSV is found without moving the data or this module.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(backend.ml_models.__file__)), "raw_project_models")
df = pd.read_csv(os.path.join(DATA_DIR, "merged2.csv"))

def line_of_best_fit(X, y):
    model = LinearRegression(fit_intercept = True)
    model.fit(X, y)
    return np.concatenate([[model.intercept_], model.coef_])

def linreg_predict(X, y, b):
    X_with_intercept = np.column_stack([np.ones(len(X)), X])
    y_pred = X_with_intercept @ b
    mse = float(np.mean((y - y_pred) ** 2))
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = float(1 - ss_res / ss_tot)
    return {"mse": mse, "r2": r2}

def train():
    cols = [
    'crime_rate', 'noise_rate', 'pollution_rate', 'hpi_weight',
    'deg_urb_Rural areas', 'deg_urb_Towns and suburbs', 'crime_noise', 'poll_noise', 'crime_hpi', 'poll_crime'
    ]
    X = np.array(df[cols])
    y = np.array(df['happy_rate'])

    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size=0.3, random_state=42)

    scaler = StandardScaler()
    Xtrain_scaled = scaler.fit_transform(Xtrain)
    Xtest_scaled = scaler.transform(Xtest)

    b = line_of_best_fit(Xtrain_scaled, ytrain)
    results = linreg_predict(Xtest_scaled, ytest, b)

    current_app.logger.info(f"train mse={results['mse']:.4f} r2={results['r2']:.4f}")

    b_str = '[' + ','.join(map(str, b)) + ']'
    scaler_mean_str = '[' + ','.join(map(str, scaler.mean_)) + ']'
    scaler_std_str = '[' + ','.join(map(str, scaler.scale_)) + ']'

    with get_db().cursor() as cursor:
        cursor.execute(
            '''INSERT INTO student_model_params
               (beta_vals, scaler_mean, scaler_std)
               VALUES (%s, %s, %s)''',
            (b_str, scaler_mean_str, scaler_std_str)
        )
    get_db().commit()

    return {'mse': results['mse'], 'r2': results['r2']}


def test():
    """
    Retrieves stored model parameters from the DB and evaluates them
    on the held-out test set.
 
    Returns:
        dict with mse and r2
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            '''SELECT beta_vals, scaler_mean, scaler_std
               FROM student_model_params
               ORDER BY id DESC LIMIT 1'''
        )
        row = cursor.fetchone()
 
    if row is None:
        raise ValueError("No model parameters found. Run train() first.")
 
    def parse(s):
        return np.array(list(map(float, s[1:-1].split(','))))
 
    b = parse(row['beta_vals'])
    scaler_mean = parse(row['scaler_mean'])
    scaler_std = parse(row['scaler_std'])
 
    df = pd.read_csv(os.path.join(DATA_DIR, "merged2.csv"))
 
    X = np.array(df[cols]).astype(float)
    y = np.array(df['happy_rate'])
 
    _, Xtest, _, ytest = train_test_split(X, y, test_size=0.3, random_state=42)
 
    Xtest_scaled = (Xtest - scaler_mean) / scaler_std
    results = linreg_predict(Xtest_scaled, ytest, b)
 
    current_app.logger.info(f"test mse={results['mse']:.4f} r2={results['r2']:.4f}")
    return {'mse': results['mse'], 'r2': results['r2']}
 
 
def predict(crime, noise, pollution, hpi, is_rural, is_towns):
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            '''SELECT beta_vals, scaler_mean, scaler_std
               FROM student_model_params
               ORDER BY id DESC LIMIT 1'''
        )
        db_row = cursor.fetchone()

    if db_row is None:
        raise ValueError("No model parameters found. Run train() first.")

    def parse(s):
        return np.array(list(map(float, s[1:-1].split(','))))

    b = parse(db_row['beta_vals'])
    scaler_mean = parse(db_row['scaler_mean'])
    scaler_std = parse(db_row['scaler_std'])

    # all country predictions
    df_latest = (                          # 1. was df = df — can't reassign global
        df.sort_values('year', ascending=False)
        .groupby('geo', as_index=False)
        .first()
    )

    results = []
    for _, r in df_latest.iterrows():
        # use country's real data only
        c_dict = {
            'crime_rate':                r['crime_rate'],
            'noise_rate':                r['noise_rate'],
            'pollution_rate':            r['pollution_rate'],
            'hpi_weight':                r['hpi_weight'],
            'deg_urb_Rural areas':       float(r['deg_urb_Rural areas']),
            'deg_urb_Towns and suburbs': float(r['deg_urb_Towns and suburbs']),
            'crime_noise':               r['crime_rate'] * r['noise_rate'],
            'poll_noise':                r['pollution_rate'] * r['noise_rate'],
            'crime_hpi':                 r['crime_rate'] * r['hpi_weight'],
            'poll_crime':                r['pollution_rate'] * r['crime_rate'],
        }

        X_input = np.array([c_dict[col] for col in cols]).astype(float)
        X_scaled = (X_input - scaler_mean) / scaler_std
        input_array = np.concatenate([[1.0], X_scaled])
        base_score = float(np.dot(b, input_array))

        # apply user preference penalties
        # higher slider = less tolerant = bigger penalty for high values
        crime_penalty     = (crime / 100)     * (r['crime_rate'] / 37.3)
        noise_penalty     = (noise / 100)     * (r['noise_rate'] / 55.9)
        pollution_penalty = (pollution / 100)  * (r['pollution_rate'] / 43.1)
        hpi_penalty       = (hpi / 100)       * (abs(r['hpi_weight']) / 14.3)

        total_penalty = (crime_penalty + noise_penalty + pollution_penalty + hpi_penalty) / 4
        adjusted_score = base_score - total_penalty

        results.append({
            'geo': r['geo'],
            'predicted_score': round(adjusted_score, 2),
        })

    X_input = np.array([c_dict[col] for col in cols]).astype(float)  # 3. was input_dict, cols
    X_scaled = (X_input - scaler_mean) / scaler_std
    input_array = np.concatenate([[1.0], X_scaled])
    prediction = float(np.dot(b, input_array))

    results.append({
        'geo': r['geo'],              # 4. was row_data
        'predicted_score': round(prediction, 2),
    })

    results.sort(key=lambda x: x['predicted_score'], reverse=True)

    # deduplicate by country
    seen = set()
    unique_results = []
    for r in results:
        if r['geo'] not in seen:
            seen.add(r['geo'])
            unique_results.append(r)

    return prediction, unique_results