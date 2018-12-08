# COPENS Two

This is project is to update the original COPENS with new features and codebase.

## Getting started

### Prerequisites
`Docker` and `docker-compose`

### Installing
`docker-compose up --build`

You'll need an account to upload and do searches and stuff, so:

1. `docker-compose exec web bash`
2. `python manage.py createsuperuser`
3. Go to `127.0.0.1:8000`

You'll have to upload a corpus first.

### Functions
#### Searching
url: `/user/search/`