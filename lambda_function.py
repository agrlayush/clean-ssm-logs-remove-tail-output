import boto3
import re

s3_client = boto3.client('s3')

def remove_tail_output(content):
    """
    Remove outputs of 'tail' commands from the log content.
    add a message indicating the number of lines removed.
    Stop at ^C, ^c.
    """
    processed_lines = []
    skip_tail_output = False
    tail_line_count = 0
    i = 0

    for line in content.splitlines():
        i += 1
        # Check for start of tail command
        if not skip_tail_output and re.search(r'# (tail|less)', line):
            skip_tail_output = True
            tail_line_count = 0  # Reset the line count for the current tail command
            processed_lines.append(line)  # Keep the 'tail' command line
            print(f"tail/less found at line {i}")
            continue

        # If skipping output, count lines until termination patterns are found
        if skip_tail_output:
            tail_line_count += 1
            if re.search(r'\^c|\^C|;[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+:', line):
                skip_tail_output = False
                # Add the termination line and a message about deleted lines
                processed_lines.append(line)
                processed_lines.append(f"*** {tail_line_count} lines of 'tail/less' output removed to save space ***")
                print(f"end found at line {i}, {tail_line_count} lines removed")
            continue

        # Add line if not in skip mode
        processed_lines.append(line)

    return '\n'.join(processed_lines)

def lambda_handler(event, context):
    try:
        # Get bucket and object key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']

        # Read the file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read()

        # Attempt decoding with UTF-8, fallback to ISO-8859-1
        try:
            decoded_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            decoded_content = file_content.decode('latin-1')  # Fallback encoding

        # Process the file content
        processed_content = remove_tail_output(decoded_content)

        # Write the processed content back to the same bucket with a new key
        processed_key = object_key.replace('.dms', '_processed.dms')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f"processed-ssm-logs/{processed_key}",
            Body=processed_content.encode('utf-8')
        )

        return {
            'statusCode': 200,
            'body': f'Processed file saved as {processed_key}'
        }
    except Exception as e:
        print(f"Error processing file: {e}")
        return {
            'statusCode': 500,
            'body': f"Error processing file: {str(e)}"
        }
