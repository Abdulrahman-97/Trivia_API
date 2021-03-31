import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from decouple import config
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        USERNAME = config('USER')
        KEY = config('KEY')
        self.database_name = "trivia_test"
        self.database_path = f'postgresql://{USERNAME}:{KEY}@localhost:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.question = {
            'question': 'Which country won the 2018 World Cup?',
            'answer': 'France',
            'category': 6,
            'difficulty':1
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """
        This function tests retrieving categories successfully.
        """
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))
    
    def test_get_paginated_questions(self):
        """
        This function tests retrieving paginated questions successfully.
        """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        """
        This function tests requesting an unavailable page.
        """
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_question(self, question_id=6):
        """
        This function tests deleting a spicific question successfully
        """
        res = self.client().delete(f"/questions/{question_id}")
        data = json.loads(res.data)
        deleted_question = Question.query\
                            .filter(Question.id == question_id)\
                            .one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertFalse(deleted_question)
    
    def test_404_delete_unavailable_question(self):
        """
        This function tests deleting an unavailable question.
        """
        res = self.client().delete("/questions/999")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
    
    def test_add_question(self):
        """
        This function tests inserting a new question successfully.
        """
        res = self.client().post("/questions", json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_add_question_none_data(self):
        """
        This function tests inserting a question with empty data or non-json.
        """
        # test empty data
        res = self.client().post("/questions", data=None)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Data is empty!')
        # test non-json
        res = self.client().post("/questions", data='data')
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Data is empty!')

    def test_add_question_invalid_format(self):
        """
        This function tests inserting a question with invalid format.
        """
        post_data = {'data': 1}
        res = self.client().post("/questions", json=post_data)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Invalid data format!')

    def test_add_question_invalid_values(self):
        """
        This function tests inserting a question with invalid values.
        """
        # test empty question
        missing_question = self.question.copy()
        missing_question['question'] = ''
        
        res = self.client().post("/questions", json=missing_question)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Question is empty!')

        # test empty answer
        missing_answer = self.question.copy()
        missing_answer['answer'] = ''
        
        res = self.client().post("/questions", json=missing_answer)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Answer is empty!')

        # test invalid category value
        invalid_category = self.question.copy()
        invalid_category['category'] = 200
        
        res = self.client().post("/questions", json=invalid_category)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Invalid category value!')

        # test invalid difficulty value
        invalid_difficulty = self.question.copy()
        invalid_difficulty['difficulty'] = 1000
        
        res = self.client().post("/questions", json=invalid_difficulty)
        data = json.loads(res.data)

        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Invalid difficulty value!')

    def test_search_questions(self):
        """
        This function tests searching questions.
        """
        # search existing search terms
        search_data = {'searchTerm': 'Peanut'}
        res = self.client().post("/questions/search", json=search_data)
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])

        # search non-existing search terms
        search_data = {'searchTerm': '2347fh8q23hg'}
        res = self.client().post("/questions/search", json=search_data)
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['total_questions'])
    
    def test_get_category_questions(self):
        """
        This function tests retrieving questions based on a category.
        """
        category = 1
        res = self.client().get(f"/categories/{category}/questions")
        data = json.loads(res.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category']['id'], category)

    def test_404_get_unavailable_category_questions(self):
        """
        This function tests retrieving questions based on an unavailable category.
        """
        category = 99
        res = self.client().get(f"/categories/{category}/questions")
        data = json.loads(res.data)
        
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 404)

    def test_select_random_question_none_data(self):    
        """
        This function tests selecting a random question with empty data
        or non-json.
        """
        res = self.client().post("/quizzes")
        data = json.loads(res.data)
        
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'No data provided!')

    def test_select_random_question_invalid_format(self):    
        """
        This function tests selecting a random question with invalid format.
        """
        post_data = {'A':'B'}
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        message = f'{post_data},\'previous_questions\' and/or \'quiz_category\' are missing!'
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], message)
    
    def test_select_random_question_invalid_values(self):    
        """
        This function tests selecting a random question with invalid values.
        """
        # test invalid quiz_category value type
        post_data = {
            'previous_questions': [],
            'quiz_category': 'quiz_1'
        }
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        message = f'{post_data},\'quiz_category\' is None or not a dictionary!'
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], message)
        # test quiz_category 'id' key missing
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'not_id': 1,
            }
        }
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        message = '\'id\' key is missing!'
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertTrue(message in data['message'])

        # test invalid quiz_category 'id' value
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': "id_1",
            }
        }
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        message = '\'id\' is not an integer!'
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertTrue(message in data['message'])

        # test invalid previous_questions value type
        post_data = {
            'previous_questions': "Q1",
            'quiz_category': {
                'type': 'Science',
                'id': 1,
            }
        }
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        message = f'{post_data["previous_questions"]}, \'previous_questions\' is not a list!'
        self.assertFalse(data['success'])
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], message)

    def test_select_random_question(self):    
        """
        This function tests selecting a random question successfully.
        """
        # test tests selecting a random question
        # with specified category
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1,
            }
        }
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

        # test tests selecting a random question
        # with unspecified category
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'all',
                'id': 0,
            }
        }
        res = self.client().post("/quizzes", json=post_data)
        data = json.loads(res.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()