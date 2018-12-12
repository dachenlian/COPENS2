# COPENS2 

This is project is to update the original COPENS with new features and codebase.

## Getting started

### Prerequisites
`Docker` and `docker-compose`

### Development
`docker-compose up --build`

To alter development settings, edit `docker-compose.override.yml`.

You'll need an account to upload and do searches and stuff, so:

1. `docker-compose exec web bash`
2. `python manage.py createsuperuser`
3. Go to `127.0.0.1:8000`

You'll have to upload a corpus first.

### Production
`docker-compose -f docker-compose.yml -f docker-compose-production.yml up -d`

This will combine base settings from `docker-compose.yml` with production settings from `docker-compose-production.yml`.

### Functions
#### Searching
url: `/user/search/`