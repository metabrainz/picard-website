"""Tests for scheduler routes"""
from website.frontend.testing import FrontendTestCase


class SchedulerViewsTest(FrontendTestCase):
    """Tests for APScheduler management routes"""

    def test_scheduler_info_returns_200(self):
        """Test GET /scheduler returns scheduler info"""
        response = self.client.get("/scheduler")
        self.assert200(response)
        data = response.json
        self.assertIn('current_host', data)

    def test_get_jobs_returns_200(self):
        """Test GET /scheduler/jobs returns job list"""
        response = self.client.get("/scheduler/jobs")
        self.assert200(response)
        data = response.json
        self.assertIsInstance(data, list)

    def test_get_nonexistent_job_returns_404(self):
        """Test GET /scheduler/jobs/<invalid> returns 404"""
        response = self.client.get("/scheduler/jobs/nonexistent")
        self.assert404(response)

    def test_delete_nonexistent_job_returns_404(self):
        """Test DELETE /scheduler/jobs/<invalid> returns 404"""
        response = self.client.delete("/scheduler/jobs/nonexistent")
        self.assert404(response)

    def test_update_nonexistent_job_returns_error(self):
        """Test PATCH /scheduler/jobs/<invalid> returns error"""
        response = self.client.patch("/scheduler/jobs/nonexistent")
        # APScheduler returns 400 for invalid job updates
        self.assertIn(response.status_code, [400, 404])

    def test_pause_nonexistent_job_returns_404(self):
        """Test POST /scheduler/jobs/<invalid>/pause returns 404"""
        response = self.client.post("/scheduler/jobs/nonexistent/pause")
        self.assert404(response)

    def test_resume_nonexistent_job_returns_404(self):
        """Test POST /scheduler/jobs/<invalid>/resume returns 404"""
        response = self.client.post("/scheduler/jobs/nonexistent/resume")
        self.assert404(response)

    def test_run_nonexistent_job_returns_404(self):
        """Test POST /scheduler/jobs/<invalid>/run returns 404"""
        response = self.client.post("/scheduler/jobs/nonexistent/run")
        self.assert404(response)

    def test_get_existing_job_returns_200(self):
        """Test GET /scheduler/jobs/<valid> returns job info"""
        # First get the list of jobs
        response = self.client.get("/scheduler/jobs")
        jobs = response.json
        if jobs:
            job_id = jobs[0]['id']
            response = self.client.get(f"/scheduler/jobs/{job_id}")
            self.assert200(response)
            data = response.json
            self.assertEqual(data['id'], job_id)

    def test_scheduler_management_endpoints_exist(self):
        """Test that scheduler management endpoints are accessible"""
        # These are POST endpoints that modify state, so we just check they exist
        # and return appropriate responses (not 404)
        management_endpoints = [
            "/scheduler/pause",
            "/scheduler/resume",
            "/scheduler/start",
        ]
        for endpoint in management_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.post(endpoint)
                # Should not be 404 (endpoint exists)
                self.assertNotEqual(response.status_code, 404)
