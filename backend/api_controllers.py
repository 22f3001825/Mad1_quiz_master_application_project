from flask_restful import Resource, Api
from flask import request, jsonify
from backend.models import db, Question

api = Api()

class QuestionListAPI(Resource):
    """Handles fetching all questions and adding a new question"""
    
    def get(self):
        questions = Question.query.all()
        return jsonify([
            {
                'id': q.id,
                'quiz_id': q.quiz_id,
                'statement': q.statement,
                'option1': q.option1.strip(),
                'option2': q.option2.strip(),
                'option3': q.option3.strip(),
                'option4': q.option4.strip(),
                'correct_option': q.correct_option,
                'explanation': q.explanation
            } for q in questions
        ])

    def post(self):
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        new_question = Question(
            quiz_id=data["quiz_id"],
            statement=data["statement"],
            option1=data["option1"].strip(),
            option2=data["option2"].strip(),
            option3=data["option3"].strip(),
            option4=data["option4"].strip(),
            correct_option=data["correct_option"],
            explanation=data.get("explanation")
        )
        db.session.add(new_question)
        db.session.commit()
        return jsonify({"message": "Question added successfully", "id": new_question.id})

class QuestionAPI(Resource):
    """Handles updating and deleting a single question"""

    def put(self, id):
        question = Question.query.get(id)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        data = request.get_json()
        question.statement = data.get("statement", question.statement)
        question.option1 = data.get("option1", question.option1)
        question.option2 = data.get("option2", question.option2)
        question.option3 = data.get("option3", question.option3)
        question.option4 = data.get("option4", question.option4)
        question.correct_option = data.get("correct_option", question.correct_option)
        question.explanation = data.get("explanation", question.explanation)

        db.session.commit()
        return jsonify({"message": "Question updated successfully"})

    def delete(self, id):
        question = Question.query.get(id)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        db.session.delete(question)
        db.session.commit()
        return jsonify({"message": "Question deleted successfully"})

# Register Routes 
api.add_resource(QuestionListAPI, '/api/questions')  # Handles GET (fetch all) and POST (add)
api.add_resource(QuestionAPI, '/api/questions/<int:id>')  # Handles PUT and DELETE
