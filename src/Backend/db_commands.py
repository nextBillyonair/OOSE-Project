from app import db

def create_db():
  db.create_all()
  return "DB Created Successfully"

def close_session():
  db.session.close()
  return "DB Session Ended"
  
def clear_db():
  db.reflect()
  db.drop_all()
  return "DB Tables dropped"
