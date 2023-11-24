import json
import uuid

from sqlalchemy import types
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import declared_attr

from miminet_model import db


class GUID(TypeDecorator):
    impl = CHAR
    __cache_ok__ = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Json(TypeDecorator):

    @property
    def python_type(self):
        return object

    impl = types.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_literal_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return None


class IdMixin(object):

    __table_args__ = {'extend_existing': True}

    id = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))


class SoftDeleteMixin(object):

    __table_args__ = {'extend_existing': True}

    is_deleted = db.Column(db.Boolean, default=False)


class TimeMixin(object):

    __table_args__ = {'extend_existing': True}

    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class CreatedByMixin(object):

    __table_args__ = {'extend_existing': True}

    @declared_attr
    def created_by_id(cls):
        return db.Column('created_by_id', db.ForeignKey('user.id'))

    @declared_attr
    def created_by_user(cls):
        return db.relationship("User")


class Test(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "test"

    name = db.Column(db.String(512), default="")
    description = db.Column(db.String(512), default="")

    sections = db.relationship("Section", back_populates="test")


class Section(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "section"

    name = db.Column(db.String(512), default="")
    description = db.Column(db.String(512), default="")
    timer = db.Column(db.DateTime, default=db.func.now())
    test_id = db.Column(db.ForeignKey("test.id"))

    test = db.relationship("Test", back_populates="sections")
    questions = db.relationship("Question", back_populates="section")
    quiz_sessions = db.relationship("QuizSession", back_populates="section")


class Question(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "question"

    question_text = db.Column(db.String(512), default="")
    question_type = db.Column(db.String(32), default="")
    section_id = db.Column(GUID(), db.ForeignKey(Section.id))

    section = db.relationship("Section", back_populates="questions")

    text_question = db.relationship('TextQuestion', back_populates='question')

    session_questions = db.relationship("SessionQuestion", back_populates="session_question")


class QuizSession(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "quiz_session"

    section_id = db.Column(GUID(), db.ForeignKey(Section.id))
    finished_at = db.Column(db.DateTime)

    section = db.relationship("Section", back_populates="quiz_sessions")
    sessions = db.relationship("SessionQuestion", back_populates="quiz_session")


class SessionQuestion(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "session_question"

    quiz_session_id = db.Column(GUID(), db.ForeignKey(QuizSession.id))
    question_id = db.Column(GUID(), db.ForeignKey(Question.id))
    answer = db.Column(db.String(8192))

    quiz_session = db.relationship("QuizSession", back_populates="sessions")
    session_question = db.relationship("Question", back_populates="session_questions")


class TextQuestion(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "text_question"

    id = db.Column(GUID(), db.ForeignKey(Question.id), primary_key=True)
    text_type = db.Column(db.String(32), default="")

    question = db.relationship('Question', back_populates='text_question')
    sorting_question = db.relationship('SortingQuestion', back_populates='text_question')
    variable_question = db.relationship('VariableQuestion', back_populates='text_question')
    matching_question = db.relationship('MatchingQuestion', back_populates='text_question')


class SortingQuestion(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "sorting_question"

    id = db.Column(GUID(), db.ForeignKey('text_question.id'), primary_key=True)
    right_sequence = db.Column(db.UnicodeText, default="")
    explanation = db.Column(db.String(512), default="")

    text_question = db.relationship('TextQuestion', back_populates='sorting_question')


class MatchingQuestion(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "matching_question"

    id = db.Column(GUID(), db.ForeignKey('text_question.id'), primary_key=True)
    map = db.Column(Json(), default="")
    explanation = db.Column(db.String(512), default="")

    text_question = db.relationship('TextQuestion', back_populates='matching_question')


class VariableQuestion(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "variable_question"

    id = db.Column(GUID(), db.ForeignKey('text_question.id'), primary_key=True)

    answers = db.relationship("Answer", back_populates="variable_question")
    text_question = db.relationship('TextQuestion', back_populates='variable_question')


class Answer(IdMixin, SoftDeleteMixin, TimeMixin, CreatedByMixin, db.Model):

    __tablename__ = "answer"

    answer_text = db.Column(db.String(512), default="")
    explanation = db.Column(db.String(512), default="")
    is_correct = db.Column(db.Boolean, default="")

    variable_question_id = db.Column(GUID(), db.ForeignKey("variable_question.id"))
    variable_question = db.relationship("VariableQuestion", back_populates="answers")
