
# University Course Management Microservice

This repository contains the **Course Management Microservice** for a larger, distributed online educational platform. The platform is designed to support various functionalities that are essential to university operations, such as course management, student enrollment, exam scheduling, grade management, and notifications. The system is currently in its early stages, with the course management microservice serving as a foundational component.

## Project Overview

The **Course Management Microservice** is responsible for handling course-related operations within the platform. It allows users (administrators, professors, and students) to perform operations such as:

- Adding new courses to the system.
- Retrieving courses based on topics or professors.
  
The platform is built using a **microservices architecture**, where different functionalities (e.g., enrollment, exams, grades, notifications) are encapsulated in their own independent services. This design allows for scalability, flexibility, and maintainability in a large and growing university ecosystem.

## Features

- **Add New Course**: Allows administrators or professors to add new courses to the platform.
- **Retrieve Courses by Topic**: Students and professors can retrieve courses based on specific topics.
- **Retrieve Courses by Professor**: Students and staff can find courses associated with specific professors.
- **Streaming Responses**: The system supports streaming responses to handle large sets of course data efficiently.

## Project Structure

This project includes the following components:

1. **FastAPI**: Used to build the RESTful API for interacting with the course management system.
2. **SQLAlchemy**: An ORM that interacts with the database to manage courses and related data asynchronously.
3. **Asynchronous Programming**: The application utilizes asynchronous programming patterns to handle I/O-bound tasks like database queries and streaming large data efficiently.
4. **Database**: A relational database (e.g., PostgreSQL) is used to store courses and their details.

## Microservice Architecture

This microservice is a part of a larger **online university platform**. The architecture is designed to break down the various functions of the university system into separate, independent services that communicate with each other through RESTful APIs. 

As the platform is still in its early stages, the **Course Management Microservice** focuses solely on course-related functionalities. However, future developments will include:

- **Student Enrollment Microservice**: Handles student registration, course enrollment, prerequisites, etc.
- **Exam Scheduling Microservice**: Manages exam schedules, locations, and student exam registrations.
- **Grade Management Microservice**: Responsible for grading and grade reports.
- **Notification Service**: Sends notifications to students and staff about course updates, exam schedules, and more.

The modularity of this architecture allows each service to be developed, deployed, and scaled independently, ensuring high availability and resilience as the platform grows.

## How to Run

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (or another relational database)
- Docker (optional, for easy database setup)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set up the Database

Ensure you have a running PostgreSQL database and update the database connection details in your environment variables.

### Run the Application

To run the FastAPI application locally:

```bash
uvicorn main:app --reload
```

### Example Endpoints

- **Add Course**
  - POST `/add_course/`
  - Body: 
  
  ```{
  "course_title": "Course Title",
  "course_description": "Course Description",
  "professor_name": "Professor Name",
  "professor_email": "professor@example.com",
  "pathway_name": "Pathway Name",
  "topic_name": "Topic Name",
  "sessions": [
    {
      "session_number": 1,
      "title": "Session Title",
      "description": "Session Description",
      "media": [
        {
          "type": "Video",
          "url": "http://example.com/video.mp4"
        }
      ]
    }
  ]}```
  
- **Get Courses by Topic**
  - GET `/courses/topic/{topic_name}`
  
- **Get Courses by Professor**
  - GET `/courses/prof/{prof_name}`

## Future Work

- **User Authentication and Authorization**: Implement secure login and role-based access control for students, professors, and administrators.
- **Event-Driven Architecture**: Introduce asynchronous event-driven architecture using message queues (e.g., Kafka, RabbitMQ) for better communication between services and to handle complex workflows like notifications or exam scheduling.
- **Microservice Expansion**: Add additional microservices for **student enrollment**, **exam management**, **grade management**, and **notification services** to complete the university platform ecosystem.

## Contributing

We welcome contributions to this project! If you'd like to contribute, please fork the repository, create a new branch, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This updated README provides context about the larger university platform, its microservices architecture, and plans for future development. It describes the course management service as an integral component of the platform, which will eventually include other services like student enrollment and exam scheduling.
