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
