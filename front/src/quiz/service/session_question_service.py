import json

from miminet_model import User, db
from quiz.entity.entity import (
    SessionQuestion,
    Answer,
    PracticeQuestion,
)
from quiz.util.dto import QuestionDto, AnswerResultDto


def get_question_by_session_question_id(session_question_id: str):
    session_question = SessionQuestion.query.filter_by(id=session_question_id).first()
    question = session_question.question
    user_id = session_question.created_by_id
    if question is None or question.is_deleted is True:
        return None, 404

    return QuestionDto(user_id, question), 200


def check_task(task_dict, answer):
    nodes = answer["nodes"]
    edges = answer["edges"]
    packets = answer["packets"]

    task = task_dict["task"]
    if task == "ping 1 host":
        from_node = task_dict["from"]
        to_node = task_dict["to"]

        request = []
        reply = []

        for packet in packets:

            type = packet[0]["config"]["type"]
            source = packet[0]["config"]["source"]
            target = packet[0]["config"]["target"]

            if "ICMP echo-request" in type:
                if not request:
                    request.append(source)
                    request.append(target)

                if request[-1] != source:
                    request.append(source)

                if request[-1] != target:
                    request.append(target)

            elif "ICMP echo-reply" in type:
                if not reply:
                    reply.append(source)
                    reply.append(target)

                if reply[-1] != source:
                    reply.append(source)

                if reply[-1] != target:
                    reply.append(target)

            else:
                continue

        if request and reply and request[0] == from_node and request[-1] == to_node and reply[0] == to_node and reply[-1] == from_node:
            return True
        else:
            return False


def answer_on_session_question(
    session_question_id: str, answer_string: dict, user: User
):
    session_question = SessionQuestion.query.filter_by(id=session_question_id).first()
    if session_question.created_by_id != user.id:
        return None, 403
    question = session_question.question
    if question.question_type == "text":
        pass
        # text_question = TextQuestion.query.filter_by(id=question.id).first()
        #
        # if text_question.text_type == "variable":
        #     explanation_list = []
        #     answers = answer_string["answer"]
        #     is_correct = True
        #     correct_count = 0
        #     answer_count = 0
        #     for check in answers:
        #         answer = Answer.query.filter_by(
        #             variable_question_id=text_question.id,
        #             answer_text=check["answer_text"],
        #         ).first()
        #         explanation_list.append(answer.explanation)
        #         answer_count += 1
        #         if not answer.is_correct:
        #             is_correct = False
        #     for _ in Answer.query.filter_by(
        #         variable_question_id=text_question.id, is_correct=True
        #     ).all():
        #         correct_count += 1
        #     correct = is_correct and answer_count == correct_count
        #     session_question.is_correct = correct
        #     db.session.add(session_question)
        #     db.session.commit()
        #
        #     return AnswerResultDto(explanation_list, correct), 200
        #
        # elif text_question.text_type == "matching":
        #     matching_question = MatchingQuestion.query.filter_by(
        #         id=text_question.id
        #     ).first()
        #     correct = matching_question.map == answer_string["answer"]
        #     session_question.is_correct = correct
        #     db.session.add(session_question)
        #     db.session.commit()
        #
        #     return AnswerResultDto(matching_question.explanation, correct), 200
        #
        # elif text_question.text_type == "sorting":
        #     sorting_question = SortingQuestion.query.filter_by(
        #         id=text_question.id
        #     ).first()
        #     correct = answer_string["answer"] == sorting_question.right_sequence
        #     session_question.is_correct = correct
        #     db.session.add(session_question)
        #     db.session.commit()
        #
        #     return AnswerResultDto(sorting_question.explanation, correct), 200

    elif question.question_type == "practice":
        practice_question = PracticeQuestion.query.filter_by(id=question.id).first()
        tasks = practice_question.practice_tasks
        is_correct = True
        correct_count = 0
        for task in tasks:
            result = check_task(json.loads(task.task), answer_string["answer"])
            is_correct &= result
            correct_count += 1 if result else 0

        is_correct &= correct_count == len(tasks)

        session_question.is_correct = is_correct
        db.session.add(session_question)
        db.session.commit()

        return AnswerResultDto(practice_question.explanation, is_correct), 200
