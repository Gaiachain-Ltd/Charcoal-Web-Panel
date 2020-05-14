# -*- coding: utf-8 -*-
import base64
import os
import requests

from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from google.protobuf.message import DecodeError
from protos.payload_pb2 import SCPayload


class TransactionListView(APIView):

    def get(self, request):
        http = 'https' if request.is_secure() else 'http'
        r = requests.get(f"{http}://{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}/transactions?{request.GET.urlencode()}")
        transactions = r.json()
        for transaction in transactions['data']:
            payload = base64.b64decode(transaction['payload'])
            try:
                t = SCPayload()
                t.ParseFromString(payload)

                payload = str(t).replace('\n', '</br>')
                if t.timestamp:
                    # Ivory Coast TZ is UTC/GMT 0. There are no Daylight Saving Time clock changes.
                    readable_timestamp = datetime.utcfromtimestamp(t.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    payload = payload.replace(str(t.timestamp), readable_timestamp)
                transaction['payload'] = payload
            except DecodeError:
                transaction['payload'] = 'System transaction'
        return Response(transactions)
