class CourseAlreadyExistsError(Exception):
    """Exception raised when a course already exists."""

    def __init__(
        self, course_id: str, message: str = "Course already exists with this ID"
    ):
        self.course_id = course_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.course_id}"


class CourseNotFoundError(Exception):
    def __init__(
        self, course_id: str, message: str = "Course doesn't exists with this ID"
    ):
        self.course_id = course_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.course_id}"


class EntityNotFoundError(Exception):
    """Custom exception for entity not found errors."""

    def __init__(self, entity_type: str, name: str):
        self.message = f"{entity_type} with name '{name}' not found."
        super().__init__(self.message)


class EntityAlreadyExistsError(Exception):
    """Custom exception for entity already existing errors."""

    def __init__(self, entity_type: str, name: str):
        self.message = f"{entity_type} with name '{name}' already exists."
        super().__init__(self.message)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
