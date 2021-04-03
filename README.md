# Full Stack API Final Project

## Full Stack Trivia

Trivia is a questions and answers application where the user can:

1) Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer. 
2) Delete questions.
3) Add questions and require that they include question and answer text.
4) Search for questions based on a text query string.
5) Play the quiz game, randomizing either all questions or within a specific category. 

## Getting Started
------------------
### Prerequisites
- Python3
- PIP
- Node
### Backend
---------
**Virtual Environment**
- Create a Virtual Environment in backend directory
```bash
python3 -m venv /path/to/new/virtual/environment
```
- Activate venv
```bash
$ source <venv>/bin/activate
```
> [Creation and Activation of virtual environments](https://docs.python.org/3/library/venv.html)

**PIP Dependencies**

Now you have your venv created and activated, navigate to the ```/backend``` directory and run the following command to install all required packages:

```bash
pip install -r requirements.txt
```

**Database Setup**
- Create trivia database, and restore the database provided 
```bash
dropdb trivia
createdb trivia
psql trivia < trivia.psql
```
- Create ```.env``` file to store environment variables for the database
```bash
touch .env
```
- Open ```.env``` and store the following:
```
USER={USERNAME}
KEY={PASSWORD}
```
**Running the server**
```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

### Frontend
-------------
**Installing Node and NPM**

Install Node and NPM from https://nodejs.org/en/download.

**Installing project dependencies**

in ```/frontend```, run the following command to install the required packages:

```bash
npm install
```
**Running the frontend**

```bash
npm start
```
By default, the frontend will run on ```127.0.0.1:3000```
### Testing
------
To run the tests, run the following:
```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Reference
------------
### Getting Started
- Base URL: The backend app is hosted locally at ```127.0.0.1:5000```
- Authentication: No authentication required
### Error Handling
Errors are returned as JSON objects as shown below:
```
{
    "success": False, 
    "error": 404,
    "message": "resource not found!"
}
```
> Some errors' formats are customized depending on the error type. 

The API will return one of the following error types when a request fails:
- 404: Not Found
- 422: Unprocessable
- 400: Bad Request
- 405: Method Not Allowed

### Endpoints
**GET /categories**
- General:
    - returns a list of categories, total number od categories, anda a success value
- Sample: ```curl 127.0.0.1:5000/categories```
```
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true,
  "total_categories": 6
}

```
**GET /questions, /questions?page=<page_number>**
- General:
    - Returns a list of question objects, categories, current category, success value, and total number of questions
    - Results are paginated in groups of 10
    - A page can be selected in a request argument(default value is 1)
- Sample: ```curl 127.0.0.1:5000/questions```
```
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": null,
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?"
    },
    ...
  ],
  "success": true,
  "total_questions": 21
}
```

**POST /questions**
- General:
    - Creates a new question using the submitted question, answer, difficulty, and category
    - Returns a success value
- Sample:
```
curl -X POST 127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{"question": "In bowling, what is the term used for getting three consecutive strikes?", "answer": "Turkey", "category": 6, "difficulty": 3}'
```
```
{
  "success": true
}
```

**DELETE /questions/<question_id>**
- General:
    - Deletes the question of the given question ID if it exists
    - Returns a success value
- Sample: ```curl -X DELETE 127.0.0.1:5000/questions/30```
```
{
  "success": true
}
```

**POST /questions/search, /questions/search?category=<category_id>**
- General:
    - Searches for questions containing the provided search term
    - Returns a list of matching questions, total number of questions, and a success value
- Sample: 
```
curl -X POST 127.0.0.1:5000/questions/search?category=1 -H "Content-Type: application/json" -d '{"searchTerm": "pen"}'
```
```
{
  "questions": [
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    }
  ],
  "success": true,
  "total_questions": 1
}
```

**GET /categories/<cat_id>/questions**
- General:
    - Returns current category, list of questions of the specified category, total number of quesitons, and a success value
- Sample: ```curl 127.0.0.1:5000/categories/6/questions```
```
{
  "current_category": {
    "id": 6,
    "type": "Sports"
  },
  "questions": [
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ],
  "success": true,
  "total_questions": 2
}
```

**POST /quizzes**
- General:
    - Selects a random question based on a category if specified, and previous questions to eleminate repetition
    - Returns a question object and a success value
- Sample: 
```
curl -X POST http://127.0.0.1:5000/quizzes -H "Content-Type: application/json" -d '{"previous_questions":[], "quiz_category": {"id": 1, "type": "Science"}}'
```
```
{
  "question": {
    "answer": "Hg",
    "category": 1,
    "difficulty": 2,
    "id": 27,
    "question": "What is the elemental symbol for mercury?"
  },
  "success": true
}

```

