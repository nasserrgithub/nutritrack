from flask import Blueprint, render_template
from nutritrack.db.database import get_session
from nutritrack.db.models import UserModel, FoodModel, FoodEntryModel

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/", methods=["GET"])
def dashboard():
    with get_session() as session:
        user_count = session.query(UserModel).count()
        food_count = session.query(FoodModel).count()
        entry_count = session.query(FoodEntryModel).count()

    return render_template(
        "admin/dashboard.html",
        user_count=user_count,
        food_count=food_count,
        entry_count=entry_count,
    )


@bp.route("/users", methods=["GET"])
def users():
    users = []
    with get_session() as session:
        users = [
            {
                "id": u.id,
                "email": u.email,
                "activity_level": u.activity_level,
                "is_active": u.is_active,
                "created_at": u.created_at,
            }
            for u in session.query(UserModel).all()
        ]
    return render_template("admin/users.html", users=users)


@bp.route("/reports/generate/<int:user_id>", methods=["POST"])
def trigger_report(user_id: int):
    from nutritrack.worker.tasks import generate_weekly_report

    task = generate_weekly_report.delay(user_id)
    return render_template("admin/task_status.html", task_id=task.id, user_id=user_id)


@bp.route("/reports/send-email/<int:user_id>", methods=["POST"])
def trigger_email(user_id: int):
    from nutritrack.worker.tasks import send_weekly_report_email

    task = send_weekly_report_email.delay(user_id)
    return render_template("admin/task_status.html", task_id=task.id, user_id=user_id)
