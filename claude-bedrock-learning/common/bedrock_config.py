
from anthropic import AnthropicBedrock

def get_anthropic_client():

     client = AnthropicBedrock(
      aws_region="ap-southeast-2"
      )
     model = "au.anthropic.claude-haiku-4-5-20251001-v1:0"
     return client, model


    
    