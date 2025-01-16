from model import db, Rating
from app import app


# Ensure the app context is pushed
with app.app_context():
    # Clear all data except the headers
    db.session.query(Rating).delete()
    
    # Commit the changes to the database
    db.session.commit()
    print("Data deleted successfully!")
