## AI Tool Finder

AI Tool Finder is a backend application built using FastAPI that helps users discover and manage AI tools based on categories, use cases, and functionality.

## Project Overview

The objective of this project is to provide a centralized platform where users can explore various AI tools efficiently. The application exposes RESTful APIs that allow listing, searching, and managing AI tools. These APIs can later be consumed by a frontend application or other services.

## Tech Stack

- Python 3.x
- FastAPI
- SQLite
- Pydantic
- Uvicorn

## Features

- List AI tools by category
- Search AI tools by name or keyword
- Add and manage AI tool entries
- RESTful API architecture
- Auto-generated Swagger and ReDoc documentation

## Project Structure
```text
ai-tool-finder/
├── app/
│ ├── main.py
│ ├── routers/
│ ├── models/
│ └── schemas/
├── tests/
├── aitools.db
├── requirements.txt
├── .gitignore
└── README.md
```


## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai-tool-finder.git
cd ai-tool-finder
```
### 2. Create a virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run the application
```
uvicorn app.main:app --reload
```

### 5. Access API documentation

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

### Future Enhancements

- User authentication and authorization

- Frontend integration

- Advanced filtering and recommendation system

- Deployment using Docker and cloud platforms

### Author

Raj Mohan R


