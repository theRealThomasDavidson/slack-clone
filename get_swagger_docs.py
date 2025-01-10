import requests
import json
import os

def get_swagger_docs():
    """Download and save OpenAPI documentation from the FastAPI backend."""
    try:
        # Get the OpenAPI JSON from FastAPI's openapi.json endpoint
        response = requests.get('http://localhost:8000/openapi.json')
        response.raise_for_status()
        
        # Save the raw JSON
        with open('openapi.json', 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, indent=2)
        
        print('✓ Successfully downloaded and saved OpenAPI documentation to openapi.json')
        
        # Also save a more readable version
        with open('API_REFERENCE.md', 'w', encoding='utf-8') as f:
            f.write('# API Reference\n\n')
            api_docs = response.json()
            
            # Write server info
            f.write('## Server Information\n')
            if 'servers' in api_docs:
                for server in api_docs['servers']:
                    f.write(f"- {server.get('description', 'Server')}: `{server.get('url')}`\n")
            f.write('\n')
            
            # Write endpoints grouped by tag
            f.write('## Endpoints\n\n')
            paths = api_docs['paths']
            for path, methods in paths.items():
                for method, details in methods.items():
                    f.write(f"### {method.upper()} {path}\n\n")
                    if 'summary' in details:
                        f.write(f"{details['summary']}\n\n")
                    if 'description' in details:
                        f.write(f"{details['description']}\n\n")
                    
                    # Parameters
                    if 'parameters' in details:
                        f.write('**Parameters:**\n\n')
                        for param in details['parameters']:
                            f.write(f"- `{param['name']}` ({param['in']}): {param.get('description', '')}\n")
                        f.write('\n')
                    
                    # Request body
                    if 'requestBody' in details:
                        f.write('**Request Body:**\n\n')
                        f.write('```json\n')
                        f.write(json.dumps(details['requestBody'], indent=2))
                        f.write('\n```\n\n')
                    
                    # Responses
                    if 'responses' in details:
                        f.write('**Responses:**\n\n')
                        for status, response in details['responses'].items():
                            f.write(f"- {status}: {response.get('description', '')}\n")
                        f.write('\n')
                    
                    f.write('---\n\n')
        
        print('✓ Successfully generated readable API documentation in API_REFERENCE.md')
        
    except requests.exceptions.RequestException as e:
        print(f'Error downloading OpenAPI documentation: {str(e)}')
        print('Make sure the FastAPI backend is running on http://localhost:8000')
    except Exception as e:
        print(f'Error processing OpenAPI documentation: {str(e)}')

if __name__ == '__main__':
    get_swagger_docs() 