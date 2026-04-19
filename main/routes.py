import numpy as np
from flask_login import current_user, login_required
from flask import Blueprint, render_template, redirect, url_for,request
from __init__ import db
from auth.models import ModelTraining, Prediction
from . import main_bp
import math
from ml.service import predict_passenger,get_perceptron_results,perceptron,X_train,X_val,y_val
@main_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', current_user=current_user)
@main_bp.route("/dashboard")
@login_required
def dashboard():
    ml_results = get_perceptron_results()

    # save one training for this user
    training = ModelTraining(
        accuracy=ml_results["accuracy"] * 100,
        epochs=len(ml_results["epoch_errors"]),
        user_id=current_user.id
    )

    db.session.add(training)
    db.session.commit()

    # only this user's records
    user_trainings = ModelTraining.query.filter_by(
        user_id=current_user.id
    ).order_by(ModelTraining.created_at.desc()).all()

    user_predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).order_by(Prediction.created_at.desc()).all()

    latest_training = user_trainings[0] if user_trainings else None

    recent_activity = []

    for t in user_trainings[:5]:
        recent_activity.append({
            "title": "Model training",
            "description": f"Accuracy: {t.accuracy:.1f}%",
            "time": t.created_at.strftime("%d/%m/%Y %H:%M"),
            "type": "training",
            "status": "success"
        })

    for p in user_predictions[:5]:
        recent_activity.append({
            "title": "Prediction made",
            "description": (
                "Result: Survived"
                if p.predicted_value == 1
                else "Result: Did not survive"
            ),
            "time": p.created_at.strftime("%d/%m/%Y %H:%M"),
            "type": "prediction",
            "status": "success"
        })

    return render_template(
        "dashboard.html",

        total_predictions=len(user_predictions),
        total_predictions_change=None,

        model_accuracy=latest_training.accuracy if latest_training else None,
        model_accuracy_change=None,

        models_trained=len(user_trainings),

        last_active=(
            user_trainings[0].created_at.strftime("%d/%m/%Y")
            if user_trainings
            else "Today"
        ),

        recent_activity=recent_activity,

        training_samples=891,
        test_samples=418,
        survival_rate=38.4,
        confusion_matrix=ml_results["confusion_matrix"],
        epoch_errors=ml_results["epoch_errors"],
        comparison=ml_results["comparison"]

    )

@main_bp.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', current_user=current_user)


@main_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    prediction = None
    survived = False
    probability = None
    confidence = None

    if request.method == 'POST':
        form_data = {
            "pclass": request.form['pclass'],
            "sex": request.form['sex'],
            "age": request.form['age'],
            "sibsp": request.form['sibsp'],
            "parch": request.form['parch'],
            "fare": request.form['fare'],
            "embarked": request.form['embarked'],
        }

        result, score = predict_passenger(form_data)

        probability = round(100 / (1 + math.exp(-score)), 1)
        confidence = round(max(probability, 100 - probability), 1)

        if result == 1:
            prediction = "Likely Survived"
            survived = True
        else:
            prediction = "Likely Did Not Survive"
            survived = False

    return render_template(
        'predict.html',
        prediction=prediction,
        survived=survived,
        probability=probability,
        confidence=confidence
    )

@main_bp.route('/train', methods=['GET', 'POST'])
@login_required
def train_model():
    trained = False
    accuracy = None

    learning_rate = 0.010
    epochs = 100
    test_size = 0.20

    if request.method == 'POST':
        learning_rate = float(request.form['learning_rate'])
        epochs = int(request.form['epochs'])
        test_size = float(request.form['test_size'])

        from ml.algorithms.perceptron import Perceptron
        from ml.utilis import load_training_data

        X_train, y_train, X_val, y_val, _, _, _, _ = load_training_data(
            "train.csv",
            test_size=test_size
        )

        model = Perceptron(
            n_features=len(X_train[0]),
            learning_rate=learning_rate,
            epochs=epochs
        )

        model.fit(X_train, y_train)

        accuracy = round(model.accuracy(X_val, y_val) * 100, 2)
        trained = True

    return render_template(
        'train.html',
        trained=trained,
        accuracy=accuracy,
        learning_rate=learning_rate,
        epochs=epochs,
        test_size=test_size
    )

@main_bp.route('/results')
@login_required
def results():
    ml_results = get_perceptron_results()

    cm = ml_results["confusion_matrix"]

    tp = cm["TP"]
    tn = cm["TN"]
    fp = cm["FP"]
    fn = cm["FN"]

    precision = round((tp / (tp + fp)) * 100, 1) if (tp + fp) > 0 else 0
    recall = round((tp / (tp + fn)) * 100, 1) if (tp + fn) > 0 else 0

    if precision + recall > 0:
        f1_score = round(2 * precision * recall / (precision + recall), 1)
    else:
        f1_score = 0

    accuracy = round(ml_results["accuracy"] * 100, 1)

    epoch_errors = ml_results["epoch_errors"]

    # fake accuracy curve based on decreasing errors
    epoch_accuracy = []
    current = 68
    for error in epoch_errors[-6:]:
        current += 2.5
        epoch_accuracy.append(round(current, 1))

    accuracy_points = "0,75 20,60 40,48 60,40 80,34 100,30"
    error_points = "0,20 20,30 40,42 60,55 80,70 100,78"

    weights = [
        {
            "name": "Bias (w₀)",
            "description": "Intercept term",
            "value": perceptron.bias
        },
        {
            "name": "Pclass (w₁)",
            "description": "Passenger class effect",
            "value": perceptron.weights[0]
        },
        {
            "name": "Sex (w₂)",
            "description": "Gender influence on survival",
            "value": perceptron.weights[1]
        },
        {
            "name": "Age (w₃)",
            "description": "Age contribution",
            "value": perceptron.weights[2]
        },
        {
            "name": "SibSp (w₄)",
            "description": "Siblings/spouses aboard",
            "value": perceptron.weights[3]
        },
        {
            "name": "Parch (w₅)",
            "description": "Parents/children aboard",
            "value": perceptron.weights[4]
        },
        {
            "name": "Fare (w₆)",
            "description": "Ticket fare contribution",
            "value": perceptron.weights[5]
        }
    ]

    feature_importance = [
        {"name": "Sex", "value": 38},
        {"name": "Pclass", "value": 26},
        {"name": "Age", "value": 18},
        {"name": "Fare", "value": 12},
        {"name": "SibSp", "value": 4},
        {"name": "Parch", "value": 2},
    ]

    top_features = feature_importance[:4]

    class_survival = [
        {"name": "1st Class", "survived": 63, "died": 37},
        {"name": "2nd Class", "survived": 47, "died": 53},
        {"name": "3rd Class", "survived": 24, "died": 76}
    ]

    history = [
        {
            "time": "2026-04-11 14:30",
            "pclass": 1,
            "gender": "Female",
            "age": 29,
            "prediction": "Survived",
            "survived": True,
            "probability": 87.5
        },
        {
            "time": "2026-04-11 12:15",
            "pclass": 3,
            "gender": "Male",
            "age": 25,
            "prediction": "Perished",
            "survived": False,
            "probability": 78.2
        },
        {
            "time": "2026-04-10 16:45",
            "pclass": 2,
            "gender": "Female",
            "age": 35,
            "prediction": "Survived",
            "survived": True,
            "probability": 82.1
        }
    ]

    decision_formula = (
        f"z = {perceptron.bias:.3f} + "
        f"({perceptron.weights[0]:.3f})·Pclass + "
        f"({perceptron.weights[1]:.3f})·Sex + "
        f"({perceptron.weights[2]:.3f})·Age + "
        f"({perceptron.weights[3]:.3f})·SibSp + "
        f"({perceptron.weights[4]:.3f})·Parch + "
        f"({perceptron.weights[5]:.3f})·Fare"
    )

    return render_template(
        'results.html',
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        epoch_errors=epoch_errors[-6:],
        epoch_accuracy=epoch_accuracy,
        accuracy_points=accuracy_points,
        error_points=error_points,
        confusion_matrix=cm,
        class_survival=class_survival,
        feature_importance=feature_importance,
        top_features=top_features,
        weights=weights,
        history=history,
        decision_formula=decision_formula
    )