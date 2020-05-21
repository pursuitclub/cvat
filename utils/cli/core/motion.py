from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json
import logging
import time
from google.cloud import storage
from core.core import CLI
from core.definition import ResourceType

log = logging.getLogger(__name__)

LABEL_JSON = json.loads("""
[
    {
        "name": "Person",
        "attributes": [
            {
                "name": "Mirror",
                "input_type": "checkbox",
                "mutable": false,
                "values": [
                    "false"
                ]
            },
            {
                "name": "Occluded",
                "input_type": "checkbox",
                "mutable": true,
                "values": [
                    "false"
                ]
            },
            {
                "name": "Truncated",
                "input_type": "checkbox",
                "mutable": true,
                "values": [
                    "false"
                ]
            }
        ]
    }
]
""")


class MotionCLI(CLI):

    def tasks_sync(self, dry_run=False, **kwargs):
        """ Create a new task with the given name and labels JSON and
        add the files to it. """
        # 1. Get list of video URLs from GCP
        # 2. Sync each video
        #     - Create task
        #     - Create task data
        #     - Initialize git sync
        # 3. Move videos to "synced" bucket on GCP

        # BEGIN LOGIN HACK
        # Perform a login request with the session and capture the CSRF token.
        # The git endpoints require it.
        login_data = {
            'username': kwargs['auth'][0],
            'password': kwargs['auth'][1],
        }
        response = self.session.post(self.api.login, json=login_data)
        response.raise_for_status()

        auth_key = response.json()['key']
        self.session.headers.update({
            'Authorization': 'Token {}'.format(auth_key),
            'X-CSRFTOKEN': self.session.cookies['csrftoken'],
        })

        time.sleep(2)
        # END LOGIN HACK

        storage_client = storage.Client()
        blobs = storage_client.list_blobs('pursuit-videos')
        for blob in blobs:
            expiration = datetime.now(timezone.utc) + timedelta(minutes=10)
            signed_url = blob.generate_signed_url(expiration=expiration)

            url = self.api.tasks
            data = {
                'name': blob.name,
                'labels': LABEL_JSON,
                'bug_tracker': '',
            }
            response = self.session.post(url, json=data)
            response.raise_for_status()
            response_json = response.json()
            log.info('Created task ID: {id} NAME: {name}'.format(**response_json))
            task_id = response_json['id']
            self.tasks_data(
                task_id,
                ResourceType['REMOTE'],
                [signed_url],
                image_quality=100,
                frame_filter='step=30', # Displayed as 'Frame step' in task creation UI
                use_zip_chunks=True,
            )

            # TODO(troycarlson): Poll for data created status before cloning git repo
            # resp = self.session.get(self.api.tasks_id_status(task_id))
            # print(resp.json())
            time.sleep(10)

            # Initialize git repo
            repo_path = 'git@github.com:pursuitclub/sandbox'
            log.info('Initializing git repo for task. task_id: {}. path: {}'.format(task_id, repo_path))
            git_api_url = self.api.git_repo_create(task_id)
            git_api_data = {
                'lfs': False,
                'path': repo_path,
                'tid': task_id,
            }
            response = self.session.post(git_api_url, json=git_api_data)

            # Break while testing
            break
