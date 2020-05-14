# -*- coding: utf-8 -*-

import json
import os
import urllib.request


class APIRequests:
    @staticmethod
    def send_payload(content: bytes) -> int:
        request = urllib.request.Request(
            f"{os.environ.get('NODE_API')}/batches",
            content,
            method="POST",
            headers={"Content-Type": "application/octet-stream"},
        )
        response = urllib.request.urlopen(request)
        if response.status == 202:
            data = json.load(response)
            print(data)
        return response.status
