import time
import json
from rest_framework import status
from rest_framework.test import APITestCase


class UrlTests(APITestCase):

    def test_bad_request(self):
        response = self.client.post('/state/extract_content/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/state/extract_content/', {'bucket_name':'json_extraction_test_bucket_v2', 'file_name':'bad_file_name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        ## populate the database
        data = {"url": "https://www.apple.com/retail/storelist/"}
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## Fail because bad filter
        response = self.client.post('/state/endpoint_state_list/',{'kwargs': '{"key"bad"value"}'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        ## Fail because attribute doesnt exist
        response = self.client.post('/state/endpoint_state_list/',{'kwargs':'{"bad_filter_key":""}'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_fetch_content(self):
        ## populate the database
        data = {"url": "https://www.apple.com/retail/storelist/"}
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ## ensure extracted content doesnt exists
        self.assert_(response.data['content']['extracted_content'] is None)

        time.sleep(2) # Since we make external requests, we dont wanna get blocked
        ## attempt to fetch content already fetched
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data['force_new'] = 'True'
        data['display_extracted'] = 'True'
        ## fetch NEW content on same URL
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ## ensure extracted content exists
        self.assert_(response.data['content']['extracted_content'] is not None)


    def test_bucket_content(self):
        ## populate the database
        data = {"bucket_name": 'json_extraction_test_bucket_v2', "file_name": "apple.html"}
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ## ensure extracted content doesnt exists
        self.assert_(response.data['content']['extracted_content'] is None)

        ## attempt to save content already fetched
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data['force_new'] = 'True'
        data['display_extracted'] = 'True'
        ## fetch NEW content on same URL
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ## ensure extracted content exists
        self.assert_(response.data['content']['extracted_content'] is not None)



    def test_list_states(self):
        ## no results returned
        response = self.client.get('/state/endpoint_state_list/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        ## no results with query returned
        response = self.client.get('/state/endpoint_state_list/',{'kwargs':{"url":"https://www.apple.com/retail/storelist/"}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        ## populate the database
        data = {"url": "https://www.apple.com/retail/storelist/"}
        response = self.client.post('/state/extract_content/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## see if the state list returns results
        response = self.client.get('/state/endpoint_state_list/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ## see if the state list with query returns results
        response = self.client.post('/state/endpoint_state_list/',{'kwargs':'{"url":"https://www.apple.com/retail/storelist/"}'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
