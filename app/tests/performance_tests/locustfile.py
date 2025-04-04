import random
from typing import Optional
from locust import HttpUser, task, between

class HealthCheck(HttpUser):
    wait_time = between(10, 15)

    @task(1)
    def test_readiness(self):
        self.client.get("/api/v1/health/ready")
    
    @task(5)
    def test_liveness(self):
        self.client.get("/api/v1/health/live")


""" Generalized API endpoints for both JLP and JLS clients. Not all are necessarily usable by both (permission-based).
Ideally we could directly utilize the API wrapper implemented by eduhelx-utils,
but that is tricky when using Locust. """
class JupyterHttpUser(HttpUser):
    # Agnostic
    def get_my_user(self) -> dict:
        return self.client.get("/api/v1/users/self")
    
    # Prof only
    def list_students(self) -> list[dict]:
        return self.client.get("/api/v1/students")
    
    # Student only
    def list_my_submissions(self, assignment_id: int) -> list[dict]:
        return self.client.get("/api/v1/submissions/self", params={
            "assignment_id": assignment_id
        })
    
    # Prof only
    def list_submissions(self, assignment_id: int, student_onyen: Optional[str] = None) -> list[dict]:
        params = {
            "assignment_id": assignment_id
        }
        if student_onyen is not None: params["student_onyen"] = student_onyen
        
        return self.client.get("/api/v1/submissions", params=params)
    
    # Agnostic, different behaviors based on user identity
    def list_my_assignments(self) -> list[dict]:
        return self.client.get("/api/v1/assignments/self")
    
    # Agnostic, includes an instructor roster
    def get_course(self) -> dict:
        return self.client.get("/api/v1/course")

""" The current way JLP/JLS serverextension endpoints are designed leads to superfluous calls. """
class JLPUser(JupyterHttpUser):
    """ This is a harsh interval and should generally lead to a higher load than authentic client behavior. """
    wait_time = between(5, 10)

    def _pull_assignments_list(self) -> list[dict]:
        """ Base assignments call (JLP).
        This flow runs regardless of whether or not the client has a "current assignment" selected.
        NOTE: In the actual client, both the list assignments and current assignment flows are implemented
        as a single endpoint. For testing purposes, though, it is better to model as distinct cases.
        """
        self.get_course()
        assignments = self.list_my_assignments()
        return assignments

    @task(5)
    def test_list_assignments(self):
        """ This flow runs when an instructor is in the "list assignments" view,
        i.e., their CWD is within the class repository but not scoped to a specific assignment.
        """
        self._pull_assignments_list()
    
    @task(10)
    def test_get_current_assignment(self):
        """ This flow runs when an instructor is in the "current assignment" view,
        i.e., their CWD is scoped to a specific assignment path.
        This is weighted highly since it is the view instructors are expected to spend most of their time on.
        """
        assignments = self._pull_assignments_list()
        # Just take any random assignment as the current one. We could make this more complex and try
        # to choose an open/closed assignment, if there is one, to maximize submissions. But not too important.
        current_assignment = random.choice(assignments)
        student_submissions = self.list_submissions(current_assignment["id"])


    @task(15)
    def test_get_course_and_instructor_and_students(self):
        """ Get course/instructor/students call (JLP).
        This is weighted to be equivalent in frequency to assignment pull calls (5 + 10).
        """
        self.get_my_user()
        self.list_students()
        self.get_course()

    @task(1)
    def test_get_settings(self):
        self.client.get("/api/v1/settings")

""" The current way JLP/JLS serverextension endpoints are designed leads to superfluous calls. """
class JLSUser(JupyterHttpUser):
    """ This is a harsh interval and should generally lead to a higher load than authentic client behavior. """
    wait_time = between(5, 10)

    def _pull_assignments_list(self) -> list[dict]:
        """ Base assignments call (JLS).
        This flow runs regardless of whether or not the client has a "current assignment" selected.
        NOTE: In the actual client, both the list assignments and current assignment flows are implemented
        as a single endpoint. For testing purposes, though, it is better to model as distinct cases.
        """
        self.get_my_user()
        self.get_course()
        assignments = self.list_my_assignments()
        return assignments

    @task(5)
    def test_get_assignments(self):
        """ This flow runs when a student is in the "list assignments" view,
        i.e., their CWD is within the class repository but not scoped to a specific assignment.
        """
        self._pull_assignments_list()

    @task(10)
    def test_get_current_assignment(self):
        """ This flow runs when a student is in the "current assignment" view,
        i.e., their CWD is scoped to a specific assignment path.
        This is weighted highly since it is the view students are expected to spend most of their time on.
        """
        assignments = self._pull_assignments_list()
        current_assignment = random.choice(assignments)
        submissions = self.list_my_submissions(current_assignment["id"])

    @task(15)
    def test_get_course_and_student(self):
        """ Get course/student identity call (JLS).
        This is weighted such that it runs at equal frequency to assignment pulls (5 + 10). """
        self.get_my_user()
        self.get_course()

    @task(1)
    def test_get_settings(self):
        self.client.get("/api/v1/settings")