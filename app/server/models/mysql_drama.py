from server import db

class Drama(db.Model):
    __tablename__ = 'drama'
    # columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def find_id_by_name(cls, name):
        drama = cls.query.filter_by(name=name).first()
        if drama:
            return drama.id
        return None

class DramaScore(db.Model):
    __tablename__ = 'drama_score'
    # columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drama_id = db.Column(db.Integer, db.ForeignKey('drama.id'))
    score = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, drama_id, score):
        self.user_id = user_id
        self.drama_id = drama_id
        self.score = score

    @classmethod
    def find_score_by_ids(cls, user_id, drama_id):
        drama_score = cls.query.filter_by(user_id=user_id, drama_id=drama_id).first()
        if drama_score:
            return drama_score.score
        return None