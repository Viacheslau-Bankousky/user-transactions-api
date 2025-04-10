# User Management, Authentication & Transactions

## Project Description

This project is an API built with **FastAPI**, providing functionality for user management, authentication, and transaction processing. It also includes features for transaction data analysis and statistics.

The API includes endpoints for user management, handling transactions (refunds, deductions, rollbacks), and generating statistical analysis via asynchronous tasks.

---

![For the Love of Money](https://st5.depositphotos.com/4975243/65405/i/600/depositphotos_654051154-stock-photo-large-sum-dollars-close-beautiful.jpg)


---


## Installation and Launch

1. Clone the repository:
   ```bash
   git clone https://gitlab.com/AgaPmd/internship-task.git
   cd <your-project-folder>
   ```

2. Build and run the application using **Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. The API will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).  
   The API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## API Endpoints

### **Authentication**

- **`POST /token`**  
  Returns an access token based on provided user credentials.

---

### **User Endpoints**

#### General User Management

- **`GET /users`**  
  Retrieve a list of all users.

- **`GET /users/{user_id}`**  
  Fetch details of a single user by ID.

- **`GET /users/{user_name}`**  
  Fetch details of users by their name.

- **`GET /users/status/{user_status}`**  
  Retrieve all users filtered by their status.

- **`POST /users`**  
  Create a new user.

- **`PATCH /users/{user_id}`**  
  Update user details by providing a partial update for a specific user ID.

---

### **Transaction Endpoints**

#### General Transaction Management:

- **`GET /transactions`**  
  Retrieve all transactions.

- **`GET /transactions/{current_status}`**  
  Retrieve all transactions filtered by their current status.

#### Specific User Transactions:

- **`GET /users/{user_id}/transactions`**  
  Retrieve all transactions for a specific user.

- **`GET /users/{user_id}/transactions/{current_status}`**  
  Retrieve transactions for a specific user filtered by their status.

#### Transaction Actions:

- **`POST /users/{user_id}/transactions/refund`**  
  Create a refund (top-up) transaction for a specific user.

- **`POST /users/{user_id}/transactions/deduct`**  
  Create a deduction (withdrawal) transaction for a specific user.

- **`PATCH /users/{user_id}/transactions/{transaction_id}`**  
  Roll back a specific transaction for a user.

#### Transaction Statistics:

- **`GET /transactions/analysis/period/{weeks_count}`**  
  Perform transaction analysis over a specified number of weeks (asynchronous).

- **`GET /transactions/analysis/status/{task_id}`**  
  Get the status or results of a transaction statistics analysis task.


## Dependencies

The main dependencies used in this project include:

- [**FastAPI**](https://fastapi.tiangolo.com/): Web framework for building APIs.
- [**SQLAlchemy**](https://docs.sqlalchemy.org/): ORM for database interactions.
- [**Pydantic**](https://pydantic-docs.helpmanual.io/): Data validation and type hints.
- [**Celery**](https://docs.celeryproject.org/): Asynchronous task queue for generating transaction statistics.
- [**Uvicorn**](https://www.uvicorn.org/): ASGI server for running the FastAPI application.

All dependencies are included in the `pyproject.toml` file, and Docker handles installation and setup automatically.

---
