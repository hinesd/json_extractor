
# Simple Json Extractor API

This Project will allow you to pass in any public facing endpoint and `FETCH and EXTRACT` any valid `Json` that exists in the response. The usage is limited as it is currently only developed to interact with a local sqlite database. 


## API Reference

#### Get all url states

```http
  GET /state/state_list
  POST /state/state_list
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `display_extracted` | `string/Bool` | **optional**. adds extracted content to the response |
| `kwargs` | `string` | **optional**. valid stringified json containing database attributes for simple querying  |


#### Fetch and extract Json

```http
  POST /state/extract_content
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `url`      | `string` | **Required**. public facing endpoint we want to fetch |
| `display_extracted` | `string/Bool` | **optional**. adds extracted content to the response |
| `force_new` | `string/Bool` | **optional**. refetches an endpoint that's already been processed |



## Usage/Examples

Fetch and Extract content from the endpoint supplied
```python
import requests, json

url = "http://127.0.0.1:8000/state/extract_content/"

payload_headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}
payload = {
    "url": "https://www.apple.com/retail/storelist/",
    "headers": json.dumps(payload_headers),
    "force_new": False,
    "display_extracted": False
}
response = requests.request("POST", url, data=payload)
print(response.text)
```

return results while applying an optional filter
```python
import requests, json

url = "http://127.0.0.1:8000/state/state_list/"

payload = {
    "url": "https://www.apple.com/retail/storelist/",
    "display_extracted": False,
    "kwargs": json.dumps({"url": "https://www.apple.com/retail/storelist/"})
}
response = requests.request("POST", url, data=payload)
print(response.text)
```

