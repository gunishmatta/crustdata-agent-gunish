import re

from haystack import component
from haystack.dataclasses import ChatMessage


def parse_api_calls(text):
    api_calls = []
    patterns = [
        r"curl --location\s+'?([^']+)'?\s+--header '([^']+)' --header '([^']+)' --header '([^']+)' --data '([^']+)'",
        r"curl --location\s+'?([^']+)'?\s+--header '([^']+)' --header '([^']+)' --header '([^']+)' --query '([^']+)'"
    ]

    for line in text.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                url, auth_header, accept_header, content_type, data_or_query = match.groups()
                method = 'POST' if '--data' in line else 'GET'
                api_calls.append({
                    'method': method,
                    'url': url,
                    'headers': {
                        'Authorization': auth_header,
                        'Accept': accept_header,
                        'Content-Type': content_type if method == 'POST' else None
                    },
                    'data' if method == 'POST' else 'params': eval(data_or_query) if method == 'POST' else data_or_query
                })
    return api_calls


@component
class APIValidationComponent:
    outgoing_edges = 1

    def __init__(self):
        self.required_fields = ["url", "method", "headers"]

    @component.output_types(message=dict)
    def run(self, replies: list[ChatMessage]):
        message = replies[0]
        api_calls = parse_api_calls(message)

        validated_calls = []
        all_valid = True
        for api_call in api_calls:
            validation_status, fixed_call = self.validate_api_call(api_call)
            validated_calls.append({
                'original': api_call,
                'validated': fixed_call,
                'status': validation_status
            })
            if validation_status != 'valid':
                all_valid = False

        response = {"message": {"text": message}}
        if api_calls and not all_valid:
            response["message"]["api_calls"] = validated_calls

        print(response)
        return response

    def validate_api_call(self, api_call):
        required_headers = ['Authorization', 'Accept']
        if api_call['method'] == 'POST':
            required_headers.append('Content-Type')

        for field in self.required_fields:
            if field not in api_call:
                return "invalid", self.fix_api_call(api_call, f"Missing {field}")

        for header in required_headers:
            if header not in api_call['headers']:
                return "invalid", self.fix_api_call(api_call, f"Missing {header} header")

        if api_call['method'] == 'POST':
            if not isinstance(api_call.get('data', {}), dict):
                return "invalid", self.fix_api_call(api_call, "Invalid data format for POST")

        return "valid", api_call

    def fix_api_call(self, api_call, error):
        if "Missing url" in error:
            api_call['url'] = "default_url"
        elif "Missing method" in error:
            api_call['method'] = "GET"  # Default to GET
        elif "Missing headers" in error:
            api_call['headers'] = {}
        elif "Missing Authorization" in error:
            api_call['headers']['Authorization'] = "Token default_token"
        elif "Missing Accept" in error:
            api_call['headers']['Accept'] = "application/json"
        elif "Missing Content-Type" in error:
            api_call['headers']['Content-Type'] = "application/json"
        elif "Invalid data format for POST" in error:
            api_call['data'] = {"example": "data"}

        api_call['status'] = "fixed"
        return api_call, error
