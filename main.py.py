from fastapi import FastAPI
import mysql.connector

app = FastAPI()


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root123",
        database="hospital"
    )


@app.get("/")
def home():
    return {"message": "FastAPI running successfully"}


@app.get("/dashboard-data")
def get_dashboard_data():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1.
        cursor.execute("SELECT COUNT(*) as total_beds FROM beds")
        total_beds_res = cursor.fetchone()
        total_beds = total_beds_res['total_beds'] if total_beds_res else 0

        cursor.execute("SELECT COUNT(*) as occupied_beds FROM beds WHERE Status='Occupied'")
        occupied_beds_res = cursor.fetchone()
        occupied_beds = occupied_beds_res['occupied_beds'] if occupied_beds_res else 0

        bed_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0


        cursor.execute("SELECT AVG(DATEDIFF(DischargeDate, AdmissionDate)) as alos FROM admissions")
        alos_res = cursor.fetchone()
        alos = alos_res['alos'] if alos_res else 0


        cursor.execute("SELECT Department, COUNT(*) as count FROM admissions GROUP BY Department")
        dept_stats = cursor.fetchall()


        cursor.execute("SELECT Outcome, COUNT(*) as count FROM outcomes GROUP BY Outcome")
        outcome_stats = cursor.fetchall()

        conn.close()

        return {
            "kpis": {
                "bed_occupancy_rate": f"{round(bed_rate, 2)}%",
                "average_stay_days": round(float(alos), 2) if alos else 0,
                "occupied_count": occupied_beds,
                "total_beds": total_beds
            },
            "department_comparison": dept_stats,
            "patient_outcomes": outcome_stats
        }

    except Exception as e:
        return {"error": str(e)}