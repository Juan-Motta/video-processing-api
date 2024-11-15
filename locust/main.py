import os

from locust import HttpUser, between, task


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://35.227.224.126:10000"

    # @task
    # def upload_video(self):
    #     """Upload video using the obtained JWT token"""
    #     self.jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwiZW1haWwiOiJkdWtrZWdlaUBnbWFpbC5jb20iLCJ1c2VybmFtZSI6ImR1a2tlZ2VpIn0.yIv6sAjDXyJSQyiTOBF0rdPb74Ogq-GjXTTAWZJG58k"

    #     # Define the path to the video file
    #     video_path = "/Users/juan/Desktop/uniandes/cloud-backend-miso/videos/0b0fbe88-2308-4d92-b154-2e7705f4ad6e/video_test.mp4"

    #     # Check if the video file exists
    #     if not os.path.isfile(video_path):
    #         print("Video file not found:", video_path)
    #         return

    #     # Prepare headers and file data
    #     headers = {"Authorization": f"Bearer {self.jwt_token}"}
    #     files = {"file": open(video_path, "rb")}

    #     # Send the POST request to upload the video
    #     with self.client.post(
    #         "/api/tasks", headers=headers, files=files, catch_response=True
    #     ) as response:
    #         if response.status_code == 200:
    #             response.success()
    #             print("Video uploaded successfully.")
    #         else:
    #             response.failure(
    #                 f"Failed to upload video: {response.status_code} - {response.text}"
    #             )

    #     # Close the file after the request is complete
    #     files["file"].close()

    @task
    def login(self):
        payload = {"username": "dukkegei", "password": "abcd1234"}
        with self.client.post(
            "/api/auth/login", json=payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                print("Login successfully.")
            else:
                response.failure(f"Failed to login")
