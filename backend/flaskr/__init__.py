import os
from flask import Flask, request, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
  
  @app.route('/categories', methods=['GET'])
  def get_categories():
    """
    This function handles requesting all availabe categories.
    """
    # get all categories
    categories = Category.query.all()
    # abort if no categories available
    if not len(categories):
      abort(404)
    # format categories
    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(formatted_categories)
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    """
    This function handles requests for paginated questions.
    """
    # get all questions
    questions = Question.query.all()
    # get requested page number
    page = request.args.get('page', 1, type=int)
    # compute starting and ending question index 
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    # format questions for specific page
    formatted_questions = [question.format() for question in questions[start:end]]
    if len(formatted_questions) == 0:
      abort(404)

    # get all categories
    categories = Category.query.all()
    # format categories
    formatted_categories = {category.id: category.type for category in categories}
    current_category = None
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(questions),
      'categories': formatted_categories,
      'currentCategory': current_category
    })
 
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    """
    This function handles deleting requested question.
    """
    question = Question.query.get_or_404(question_id)
    question.delete()

    return jsonify({
      'success': True
    })

  @app.route('/questions', methods=['POST'])
  def add_question():
    """
    This function handles inserting a new question.
    """
    difficulties = [1, 2, 3, 4, 5]
    categories = get_categories().json
    
    data = request.get_json()
    # check if request data is valid
    if data is None:
      abort(400, 'Data is empty!')
    elif ('question' or 
          'answer' or 
          'category' or 
          'difficulty') not in data.keys():
      abort(400, 'Invalid data format!')
    elif len(data['question']) < 1:
      abort(400, 'Question is empty!')
    elif len(data['answer']) < 1:
      abort(400, 'Answer is empty!')
    elif data['category'] not in categories.values():
      abort(400, 'Invalid category value!')
    elif data['difficulty'] not in difficulties:
      abort(400, 'Invalid difficulty value!')  
    else:
      question = Question(data['question'],
                          data['answer'],
                          data['category'],
                          data['difficulty'])
      
      question.insert()
      
    return jsonify({
      'success': True
    })
  
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    """
    This function handles requested search for questions.
    """
    # get search term and category if selected
    search_term = request.get_json()['searchTerm']
    current_category = request.args.get('category', None, type=int)
    # check if a category is selected or not
    if current_category is None:
      questions = Question.query\
                  .filter(Question.question.ilike(f'%{search_term}%')).all()
    else:
      questions = Question.query\
                  .filter(Question.question.ilike(f'%{search_term}%'))\
                  .filter(Question.category == current_category).all()
    # format questions
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions)
    })
 
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_category_questions(cat_id):
    """
    This function handles requests for questions based on on a category.
    """
    # check category availability
    current_category = Category.query.get_or_404(cat_id)
    questions = Question.query\
                .filter(Question.category == str(cat_id))\
                .all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': current_category.format()
    })

  @app.route('/quizzes', methods=['POST'])
  def select_random_question():
    """
    This function handles the process of selecting a random question
    based on a category if specified, and previous questions
    to eleminate repetition.
    """
    data = request.get_json()
    # check if request data is valid 
    if data is not None:
      # check dictionary is in correct format
      if ('previous_questions' or 'quiz_category') not in data.keys():
        abort(400, f'{data},\'previous_questions\' and/or \'quiz_category\' are missing!')

      previous_questions = data['previous_questions']
      quiz_category = data['quiz_category']
      # check all values are valid
      if quiz_category is None or not isinstance(quiz_category, dict):
        abort(400, f'{data},\'quiz_category\' is None or not a dictionary!')
      elif not isinstance(previous_questions, list):
        abort(400, f'{previous_questions}, \'previous_questions\' is not a list!')
      elif 'id' not in quiz_category.keys():
        abort(400, f'{quiz_category}, \'id\' key is missing!')
      elif type(quiz_category['id']) is not int:
        abort(400, f'{quiz_category}, \'id\' is not an integer!')
      elif quiz_category['id'] == 0:
        question = Question.query\
                  .filter(Question.id.notin_(previous_questions))\
                  .order_by(func.random()).first()
      else:
        question = Question.query\
                  .filter(Question.category == str(quiz_category['id']))\
                  .filter(Question.id.notin_(previous_questions))\
                  .order_by(func.random()).first()
      
      formatted_question = question.format() if question is not None else None
    else:
      abort(400, 'No data provided!')

    return jsonify({
      'success': True,
      'question': formatted_question
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found!'
    }), 404
  
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable!'
    }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
    response = error.description
    return jsonify({
      'success': False,
      'error': 400,
      'message': response
    }), 400
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed!'
    }), 405

  return app

    