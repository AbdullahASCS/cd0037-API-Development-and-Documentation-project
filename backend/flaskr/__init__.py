import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from collections import Counter
from werkzeug.exceptions import HTTPException
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(database_path="",test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.app_context().push()
    if database_path:
        setup_db(app,database_path)
    else:
        setup_db(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    # helper function for formatting categories
    def format_categories(categories):
        dict_categories = {}
        for category in categories:
            dict_categories[category.id] = category.type
        return dict_categories

    # helper function for formatting questions
    def format_questions(questions):
        return list(map(lambda question: question.format(), questions))

    # helper function for getting the most common categories from a list of questions
    def most_common_category(questions):
        categories = [question['category'] for question in questions]
        counter = Counter(categories)
        frequent_category = counter.most_common(1)[0][0]  # get the id of most frequent category
        return frequent_category

    # helper function for handling errors
    def handle_error(e):
        if isinstance(e, HTTPException):
            abort(e.code)
        else:
            abort(500)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Methods ', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            if len(categories) == 0:
                abort(404)
            dict_categories = format_categories(categories)
            return jsonify({
                "categories": dict_categories
            })
        except Exception as e:
            handle_error(e)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.all()
            selected_questions = questions[start:end]
            if len(selected_questions) == 0:
                abort(404)
            formatted_questions = format_questions(selected_questions)
            return jsonify({
                'questions': formatted_questions,
                'totalQuestions': len(questions),
                'categories': format_categories(Category.query.all()),
                'currentCategory': None
            })
        except Exception as e:
            handle_error(e)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<id>', methods=['DELETE'])
    def delete_question(id):
        Question.query.get_or_404(id).delete()
        return ('', 204)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def submit_question():
        try:
            data = request.get_json()
            question = data['question']
            answer = data['answer']
            difficulty = data['difficulty']
            category = data['category']
            new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            new_question.insert()
            return '', 204
        except Exception as e:
            handle_error(e)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            data = request.get_json()
            if 'searchTerm' not in data:
                print("No search term provided")
                abort(400)
            search_term = data['searchTerm']
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%'))
            if questions.count() == 0:
                abort(404)
            formatted_questions = format_questions(questions)
            current_category_id = most_common_category(formatted_questions)
            return jsonify({
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'currentCategory': Category.query.get(current_category_id).type
            })
        except Exception as e:
            handle_error(e)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<category_id>/questions')
    def get_categorized_questions(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            total_questions = len(questions)
            if total_questions == 0:
                abort(404)
            formatted_questions = format_questions(questions)
            return jsonify({
                "questions": formatted_questions,
                "totalQuestions": total_questions,
                "currentCategory": Category.query.get(category_id).type
            })
        except Exception as e:
            handle_error(e)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quiz', methods=['POST'])
    def play_quiz():
        try:
            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']
            print(quiz_category)
            if quiz_category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=quiz_category['id'])
            upcoming_questions: list = [question for question in questions if question.id not in previous_questions]
            if len(upcoming_questions) == 0:
                abort(422)
            return jsonify({
                'question': random.choice(upcoming_questions).format()
            })
        except Exception as e:
            handle_error(e)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'errorCode': '404',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'status': 'error',
            'errorCode': '422',
            'message': 'The request cannot be processed due to an unprocessable entity'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'errorCode': '400',
            'message': 'Bad request'
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'status': 'error',
            'errorCode': '500',
            'message': 'Internal server error'
        }), 500

    return app
