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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "raw_project_models/merged2.csv"))

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
 
    df = pd.read_csv("merged2.csv")
 
    X = np.array(df[cols]).astype(float)
    y = np.array(df['happy_rate'])
 
    _, Xtest, _, ytest = train_test_split(X, y, test_size=0.3, random_state=42)
 
    Xtest_scaled = (Xtest - scaler_mean) / scaler_std
    results = linreg_predict(Xtest_scaled, ytest, b)
 
    current_app.logger.info(f"test mse={results['mse']:.4f} r2={results['r2']:.4f}")
    return {'mse': results['mse'], 'r2': results['r2']}
 
 
def predict(crime, noise, pollution, hpi, is_rural, is_towns):
    """
    Retrieves stored model parameters from the DB and returns a predicted
    life satisfaction score for the given housing inputs.
 
    Args:
        crime (float): crime rate (raw value)
        noise (float): noise rate (raw value)
        pollution (float): pollution rate (raw value)
        hpi (float): housing price index (raw value)
        is_rural (bool): True if rural area
        is_towns (bool): True if towns/suburbs (both False = cities)
 
    Returns:
        country, predicted satisfaction score (dict)
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

    results = []
    for _, row_data in df.iterrows():
        input_dict = {
            'crime_rate':                crime,
            'noise_rate':                noise,
            'pollution_rate':            pollution,
            'hpi_weight':                hpi,
            'deg_urb_Rural areas':       float(is_rural),
            'deg_urb_Towns and suburbs': float(is_towns),
            'crime_noise':               crime * noise,
            'poll_noise':                pollution * noise,
            'crime_hpi':                 crime * hpi,
            'poll_crime':                pollution * crime,
        }

        X_input = np.array([input_dict[col] for col in cols]).astype(float)
        X_scaled = (X_input - scaler_mean) / scaler_std
        input_array = np.concatenate([[1.0], X_scaled])
        prediction = float(np.dot(b, input_array))

        results.append({
            'geo': row_data['geo'],
            'predicted_score': round(prediction, 4),
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
