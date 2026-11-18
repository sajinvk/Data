import os
import truststore

def aws_env_setup():
    #"Setup AWS environment variables for the script"
    
    os.environ["AWS_PROFILE"] = "NP-DP-SysAccounts-AllPlatforms"
    os.environ["AWS_REGION"] = "ap-southeast-2"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"

    truststore.inject_into_ssl()
    