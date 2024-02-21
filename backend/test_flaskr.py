import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv, find_dotenv


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        load_dotenv(find_dotenv())
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(os.getenv("database_user"),
                                                               os.getenv("database_password"),
                                                               os.getenv("DATABASE_URL"), self.database_name)
        self.app = create_app(self.database_path)
        self.client = self.app.test_client

        # binds the app to the current context

    # with self.app.app_context():
    #     self.db = SQLAlchemy()
    #     self.db.init_app(self.app)
    #     # create all tables
    #     self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

    def test_get_question_by_404(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['status'], 'error')

    def test_delete_question(self):
        res = self.client().delete('/questions/18')
        self.assertEqual(res.status_code, 204)

    def test_delete_question_404(self):
        res = self.client().delete('/questions/100000')
        self.assertEqual(res.status_code, 404)

    def test_submit_question(self):
        res = self.client().post('/questions',
                                 json={'question': 'test', 'answer': 'test', 'category': 1, 'difficulty': 2})
        self.assertEqual(res.status_code, 204)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'what'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_search_question_400(self):
        res = self.client().post('/questions/search', json={'noSearchTerm': 'what'})
        self.assertEqual(res.status_code, 400)

    def test_search_categorized_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_play_quiz(self):
        res = self.client().post('/quiz',
                                 json={'previous_questions': [], 'quiz_category': {'id': 1, 'type': 'Science'}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_play_quiz_422(self):
        res = self.client().post('/quiz',
                                 json={'previous_questions': [i for i in range(0,100)],
                                       'quiz_category': {'id': 1, 'type': 'Science'}})
        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
