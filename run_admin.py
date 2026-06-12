from nutritrack.admin.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=True)


# from nutritrack.worker.tasks import generate_weekly_report
# result = generate_weekly_report.delay(1)
# print('Task ID:', result.id)
# print('Status:', result.status)
