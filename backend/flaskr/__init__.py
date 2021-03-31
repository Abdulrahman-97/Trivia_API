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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
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

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    """
    This function handles GET requests for /questions endpoint.
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
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.delete()

    return jsonify({
      'success': True
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    if request.get_json() is not None:
      question = Question(request.get_json()['question'],
                          request.get_json()['answer'],
                          request.get_json()['category'],
                          request.get_json()['difficulty'])
      
      question.insert()
    else:
      abort(400)

    return jsonify({
      'success': True
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.get_json()['searchTerm']
    current_category = request.args.get('category', None, type=int)
    
    if current_category is None:
      questions = Question.query\
                  .filter(Question.question.ilike(f'%{search_term}%')).all()
    else:
      questions = Question.query\
                  .filter(Question.question.ilike(f'%{search_term}%'))\
                  .filter(Question.category == current_category).all()

    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions)
    })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_category_questions(cat_id):
    current_category = Category.query.get_or_404(cat_id)
    questions = Question.query.filter(Question.category == current_category.id).all()
    formatted_questions = [question.format() for question in questions]
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': current_category.format()
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def select_random_question():
    data = request.get_json()
    print(data, type(data))
    if data is not None:
      if ('previous_questions' or 'quiz_category') not in data.keys():
        abort(400, f'{data},\'previous_questions\' and/or \'quiz_category\' are missing!')

      previous_questions = data['previous_questions']
      quiz_category = data['quiz_category']
      
      if quiz_category is None or not isinstance(quiz_category, dict):
        abort(400, f'{data},\'quiz_category\' is None or not a dictionary!')
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
                  .filter(Question.category == quiz_category['id'])\
                  .filter(Question.id.notin_(previous_questions))\
                  .order_by(func.random()).first()
      
      formatted_question = question.format() if question is not None else None
    else:
      abort(400, 'No data provided!')

    return jsonify({
      'success': True,
      'question': formatted_question
    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resource not found!'
    }), 404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable!'
    }), 422
  
  @app.errorhandler(400)
  def not_found(error):
    response = error.description
    return jsonify({
      'success': False,
      'error': 400,
      'message': response
    }), 400
  
  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'method not allowed!'
    }), 405

  return app

    