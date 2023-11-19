import json
from .models import UrlState
from .serializers import DataContentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from data_extraction.json_extractor import json_extractor
from django.core.exceptions import FieldError
import requests
import datetime


@api_view(['GET', 'POST'])
def endpoint_state_list(request):
    display_extracted = False
    if request.method == 'POST':
        data = request.data
        display_extracted = str(data.get('display_extracted', '')).lower() in ['true', '1']
        data_filter = data.get('kwargs') ## TODO break this out to be strict with filtering
        if data_filter:
            try:
                state = UrlState.objects.filter(**json.loads(data_filter))
            except FieldError as e:
                return Response({'invalid_filter_attribute': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
            except json.JSONDecodeError as e:
                return Response({'invalid_filter': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
            if state:
                content = DataContentSerializer(state, many=True, context={'display_extracted': display_extracted}).data
                ret_status = status.HTTP_200_OK
            else:
                content = [{'query_status': 'No Results'}]
                ret_status = status.HTTP_204_NO_CONTENT
            return Response({'display_extracted': display_extracted, 'content': content}, status=ret_status)
    state = UrlState.objects.all()
    if state:
        content = DataContentSerializer(state, many=True, context={'display_extracted': display_extracted}).data
        ret_status = status.HTTP_200_OK
    else:
        content = [{'query_status': 'No Results'}]
        ret_status = status.HTTP_204_NO_CONTENT
    return Response({'display_extracted': display_extracted, 'content': content}, status=ret_status)


@api_view(['POST'])
def extract_content(request):

    data = request.data
    url = data.get('url')

    display_extracted = str(data.get('display_extracted', '')).lower() in ['true', '1']
    force_new = str(data.get('force_new', '')).lower() in ['true', '1']
    # get the content state
    if url:
        unique_id = url
        state = UrlState.objects.filter(url=url)
    else:
        return Response({'status': 'URL must be supplied'}, status=status.HTTP_400_BAD_REQUEST)

    if not state or force_new:
        # fetch the content
        status_code, text, time_fetched, content_status = fetch_content(data=data, url=url)
        if not content_status['status']:
            return Response({'status': content_status['results']},status=status.HTTP_400_BAD_REQUEST)
        state, created = UrlState.objects.get_or_create(url=unique_id,time_fetched=datetime.datetime.now(),fetch_status=status_code,raw_content=text)
        extracted_data = json_extractor(text)
        if extracted_data:
            state.extracted_content = extracted_data
            state.save()

            serializer = DataContentSerializer(state, context={'display_extracted': display_extracted})
            return Response({'status': 'Content Extracted and Saved', 'display_extracted': display_extracted,
                             'content': serializer.data}, status=status.HTTP_200_OK)

        serializer = DataContentSerializer(state, context={'display_extracted': display_extracted})
        return Response({'status': 'Content Saved', 'display_extracted': display_extracted,
                         'content': serializer.data}, status=status.HTTP_206_PARTIAL_CONTENT)

    serializer = DataContentSerializer(state[0], context={'display_extracted': display_extracted})
    return Response(
        {'status': 'Content Already Exists', 'display_extracted': display_extracted, 'force_new': 'False',
         'content': serializer.data}, status=status.HTTP_204_NO_CONTENT)


def fetch_content(data, url):

    if url:
        # TODO add proxy network / alternate fetching solutions
        # TODO accept alternate METHODS dynamically based on results
        headers = data.get('headers')
        payload = data.get('payload')
        if headers:
            headers = json.loads(headers)
        if payload:
            payload = json.load(payload)
        response = requests.request("GET", url, headers=headers, data=payload)
        return (response.status_code, response.text, datetime.datetime.now(), {'status': True})
    else:
        return (None, None, None, {'status': False, 'results': 'Not sure how we got here'})
