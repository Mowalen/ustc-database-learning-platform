import enum

class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    DROPPED = "dropped"

class TaskType(str, enum.Enum):
    ASSIGNMENT = "assignment"
    EXAM = "exam"

class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    GRADED = "graded"
    LATE = "late"
