from app.database import SessionLocal
from app.services.optimizer import run_optimization

def run_all():
    db = SessionLocal()
    try:
        for sc_id in ["PUB-A", "PUB-B", "PUB-C", "CUST-A", "TEST-EXTREME"]:
            print(f"Running optimization for {sc_id}...")
            run_id = run_optimization(sc_id, db)
            print(f"Completed run: {run_id}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_all()
