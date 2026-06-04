# db.py
from flask_sqlalchemy import SQLAlchemy
from dao.model import db  

def init_db(app):
    db.init_app(app)
    
def get_session():
    return db.session

# class BaseRepository:
#     def __init__(self, model):
#         self.model = model
#         self.db = db
    
#     def get_by_id(self, id):
#         return self.model.query.get(id)
    
#     def get_all(self):
#         return self.model.query.all()
    
#     def create(self, **kwargs):
#         instance = self.model(**kwargs)
#         db.session.add(instance)
#         db.session.commit()
#         return instance
    
#     def update(self, id, **kwargs):
#         instance = self.get_by_id(id)
#         if instance:
#             for key, value in kwargs.items():
#                 setattr(instance, key, value)
#             db.session.commit()
#         return instance
    
#     def delete(self, id):
#         instance = self.get_by_id(id)
#         if instance:
#             db.session.delete(instance)
#             db.session.commit()