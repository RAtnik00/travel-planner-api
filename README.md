# Travel Planner API

A FastAPI backend for managing travel projects and places that travellers want to visit. Places are validated through the Art Institute of Chicago API before they are stored.

## Features

- Create, list, retrieve, update, and delete travel projects
- Create a project with places in a single request
- Add places to an existing project
- Validate external places through the Art Institute of Chicago API
- Add and update notes for project places
- Mark places as visited
- Automatically mark a project as completed when all its places are visited
- Prevent deleting projects that contain visited places
- Prevent duplicate external places within the same project
- Enforce a maximum of 10 places per project
- Pagination and filtering for list endpoints
- In-memory caching for Art Institute API responses
- Basic authentication
- SQLite database
- Docker support

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- httpx
- Uvicorn

## Requirements

- Python 3.12+
- pip

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger/OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Authentication

Project and place endpoints are protected with Basic Auth.

Default credentials:

```text
username: admin
password: secret
```

You can override them with environment variables:

```bash
export BASIC_AUTH_USERNAME=myuser
export BASIC_AUTH_PASSWORD=mypassword
```

## Docker

Build the Docker image:

```bash
docker build -t travel-planner-api .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e BASIC_AUTH_USERNAME=admin \
  -e BASIC_AUTH_PASSWORD=secret \
  travel-planner-api
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /
```

### Travel Projects

```http
POST /projects
GET /projects
GET /projects/{project_id}
PATCH /projects/{project_id}
DELETE /projects/{project_id}
```

`GET /projects` supports:

```text
skip
limit
completed
```

Example:

```http
GET /projects?skip=0&limit=20&completed=false
```

### Project Places

```http
POST /projects/{project_id}/places
GET /projects/{project_id}/places
GET /projects/{project_id}/places/{place_id}
PATCH /projects/{project_id}/places/{place_id}
```

`GET /projects/{project_id}/places` supports:

```text
skip
limit
visited
```

Example:

```http
GET /projects/1/places?skip=0&limit=20&visited=false
```

## Example Requests

### Create a project

```http
POST /projects
Authorization: Basic admin:secret
Content-Type: application/json
```

```json
{
  "name": "Chicago trip",
  "description": "Museum day",
  "start_date": "2026-07-10"
}
```

### Create a project with places

```http
POST /projects
Authorization: Basic admin:secret
Content-Type: application/json
```

```json
{
  "name": "Chicago museum trip",
  "description": "Artworks to visit",
  "places": [
    {
      "external_id": "129884",
      "notes": "Start here"
    }
  ]
}
```

### Add a place to a project

```http
POST /projects/1/places
Authorization: Basic admin:secret
Content-Type: application/json
```

```json
{
  "external_id": "129884",
  "notes": "Must see"
}
```

### Update notes and mark a place as visited

```http
PATCH /projects/1/places/1
Authorization: Basic admin:secret
Content-Type: application/json
```

```json
{
  "notes": "Visited on the first day",
  "visited": true
}
```

## Business Rules

- A project can contain up to 10 places.
- The same external place cannot be added to the same project more than once.
- A place must exist in the Art Institute of Chicago API before it is stored.
- A project cannot be deleted if any of its places are marked as visited.
- A project is marked as completed when all its places are marked as visited.

## External API

This project uses the Art Institute of Chicago API:

```text
https://api.artic.edu/api/v1/artworks/{id}
```

Documentation:

```text
https://api.artic.edu/docs/
```
