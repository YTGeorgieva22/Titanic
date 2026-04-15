from flask_login import current_user, login_required
from flask import Blueprint, render_template, redirect, url_for,request
from __init__ import db
from auth.models import ModelTraining, Prediction
from ml.service import get_perceptron_results
from ml.service import predict_passenger
from . import main_bp

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
        # your prediction logic here
        prediction = "Likely Survived"
        survived = True
        probability = 90.0
        confidence = 85.2

    return render_template(
        'predict.html',
        prediction=prediction,
        survived=survived,
        probability=probability,
        confidence=confidence
    )