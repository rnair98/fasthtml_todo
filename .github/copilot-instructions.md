Code Style and Structure:

- Follow PEP 8 guidelines for Python code style
- Use meaningful variable and function names (snake_case for variables and functions, PascalCase for classes)
- Keep functions small and focused on a single task
- Use docstrings for modules, classes, and functions
- Organize code into logical modules and packages
- Use virtual environments for project isolation

Python-specific Conventions:

- Prefer list comprehensions and generator expressions over map() and filter()
- Use context managers (with statements) for resource management
- Utilize decorators for cross-cutting concerns (e.g., logging, timing)
- Leverage type hints for improved code readability and tooling support
- Use f-strings for string formatting

Framework and API Development:

- Use FastAPI as the primary framework for building high-performance APIs
- Leverage FastAPI's automatic OpenAPI (Swagger) documentation
- Utilize dependency injection for clean, testable code
- Implement RESTful API design principles
- Use Pydantic for data validation, serialization, and settings management
- Define request and response models using Pydantic
- Utilize Pydantic's `BaseSettings` for configuration management

Database and Data Modeling:

- Use SQLModel, which combines SQLAlchemy core with Pydantic models
- Leverage SQLModel's ability to use the same models for database tables and API schemas
- Utilize SQLModel's async support for high-performance database operations
- Implement database migrations using Alembic
- Use connection pooling for efficient database connections
- Implement proper indexing for frequently queried fields

Authentication and Security:

- Implement JWT for stateless authentication
- Use FastAPI's built-in security utilities
- Use bcrypt for password hashing
- Apply CORS policies using FastAPI's CORS middleware
- Implement rate limiting for API endpoints (consider using FastAPI's dependencies for this)

Error Handling and Logging:

- Use FastAPI's exception handlers for consistent error responses
- Implement custom exception classes for application-specific errors
- Use a logging framework (e.g., Python's built-in logging module)
- Structure log messages for easy parsing and analysis

Frontend Development:

- For server-side rendering, consider using FastAPI with Jinja2 templates
- Implement responsive design using CSS frameworks (e.g., Bootstrap)
- For single-page applications, use a JavaScript framework (e.g., React, Vue.js) that consumes your FastAPI backend

Testing:

- Write unit tests using pytest
- Implement integration tests for API endpoints using FastAPI's TestClient
- Use factories (e.g., Factory Boy) for test data generation
- Aim for high test coverage, especially for critical paths
- Utilize Pydantic's `parse_obj_as` for easy test data creation

Asynchronous Processing:

- Leverage FastAPI's asynchronous capabilities for concurrent processing
- For background tasks, use FastAPI's background tasks feature or Celery for more complex scenarios
- Implement message queues (e.g., RabbitMQ, Redis) for task management if needed

Deployment and DevOps:

- Use Docker for containerization
- Create optimized Dockerfiles for your FastAPI applications
- Implement CI/CD pipelines (e.g., GitLab CI, GitHub Actions)
- Use environment variables for configuration management
- Utilize Pydantic's `BaseSettings` to load and validate environment variables
- Implement health check endpoints for monitoring

Performance Optimization:

- Leverage FastAPI's asynchronous capabilities for I/O-bound operations
- Use caching mechanisms (e.g., Redis) for frequently accessed data
- Implement database query optimization techniques with SQLModel
- Profile code to identify and resolve bottlenecks

API Documentation:

- Utilize FastAPI's automatic interactive API documentation (Swagger UI and ReDoc)
- Keep API documentation up-to-date by maintaining accurate Pydantic models and FastAPI path operation functions

Version Control:

- Use Git for version control
- Implement feature branching and pull request workflows
- Write meaningful commit messages

Dependencies Management

- Use pip and requirements.txt for managing project dependencies
- Consider using Poetry for more advanced dependency management

Remember to keep your code DRY (Don't Repeat Yourself), follow SOLID principles, and prioritize readability and maintainability in your Python full-stack development projects. Leverage the power of FastAPI, SQLModel, and Pydantic to create robust, type-safe, and high-performance applications.
