import csv
import io

from flask import Blueprint, render_template, Response, stream_with_context
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from nutritrack.db.database import get_session
from nutritrack.db.models import UserModel, FoodModel, FoodEntryModel
from nutritrack.db.repositories import FoodEntryRepository, UserRepository
from nutritrack.worker.tasks import generate_weekly_report

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


@bp.route("/export/food-log/<int:user_id>", methods=["GET"])
def export_food_log(user_id: int) -> Response:
    def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "food_name",
                "weight_g",
                "meal_slot",
                "logged_date",
                "calories",
                "protein",
                "carbs",
                "fat",
            ]
        )
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        with get_session() as session:
            repo = FoodEntryRepository(session)
            entries = repo.get_by_user(user_id)
            for entry in entries:
                from nutritrack.api.routers.summary import orm_to_food_entry

                fe = orm_to_food_entry(entry)
                writer.writerow(
                    [
                        entry.id,
                        entry.food.name,
                        fe.weight_g,
                        fe.meal_slot,
                        fe.logged_date,
                        round(fe.scaled_calories(), 2),
                        round(fe.scaled_protein(), 2),
                        round(fe.scaled_carbs(), 2),
                        round(fe.scaled_fat(), 2),
                    ]
                )
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

    return Response(
        stream_with_context(generate()),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=food_log_user_{user_id}.csv"
        },
    )


@bp.route("/export/weekly-report/<int:user_id>", methods=["GET"])
def export_weekly_report(user_id: int) -> Response:
    weekly_report = generate_weekly_report(user_id=user_id)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setStrokeColor(colors.black)
    c.drawString(100, 750, "NutriTrack Weekly Report")
    c.drawString(100, 720, f"User: {weekly_report['email']}")
    c.drawString(
        100, 700, f"Period: {weekly_report['start_date']} - {weekly_report['end_date']}"
    )
    c.drawString(100, 670, "Macro Summary")
    c.line(100, 650, 500, 650)
    c.drawString(100, 630, "Metric")
    c.drawString(250, 630, "Total")
    c.drawString(350, 630, "Remaining")
    c.line(100, 610, 500, 610)
    c.drawString(100, 590, "Calories")
    c.drawString(250, 590, f"{round(weekly_report['total_calories'], 2)}")
    c.drawString(350, 590, f"{round(weekly_report['remaining_calories'], 2)}")

    c.drawString(100, 570, "Protein")
    c.drawString(250, 570, f"{round(weekly_report['total_protein'], 2)}")
    c.drawString(350, 570, f"{round(weekly_report['remaining_protein'], 2)}")

    c.drawString(100, 550, "Carbs")
    c.drawString(250, 550, f"{round(weekly_report['total_carbs'], 2)}")
    c.drawString(350, 550, f"{round(weekly_report['remaining_carbs'], 2)}")

    c.drawString(100, 530, "Fat")
    c.drawString(250, 530, f"{round(weekly_report['total_fat'], 2)}")
    c.drawString(350, 530, f"{round(weekly_report['remaining_fat'], 2)}")

    c.line(100, 510, 500, 510)
    c.drawString(
        100, 490, f"Food entries logged this week: {weekly_report['entry_count']}"
    )

    c.save()
    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=weekly_report_user_{user_id}.pdf"
        },
    )
