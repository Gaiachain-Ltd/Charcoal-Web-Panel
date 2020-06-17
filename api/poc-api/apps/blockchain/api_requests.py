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
        data = json.load(response)
        if response.status == 202:
            print(data)
        return data
