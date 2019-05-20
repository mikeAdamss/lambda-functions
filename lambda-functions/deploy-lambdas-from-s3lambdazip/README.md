

** NOTE - this the the initial mvp implementation and required manual creation via the console.**

### deploy-lambdas-from-s3lambdazip
Uses: node

A simple lambda function that deploys other lambda functions when the zip files representing them are uploaded
to an s3 bucket.

## Setting up this Lambda

- Upload or paste the contents of index.js into the lambda inline editor for node.
- Create an s3 bucket trigger - select bucket name - set suffix to ".zip"
- Create and add the following policies to its permissions.

Allow deployment of other lambda functions.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "lambda:UpdateFunctionCode",
            "Resource": "arn:aws:lambda:*:*:function:*"
        }
    ]
}
```

Allow read access to the s3 bucket.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::<NAME_OF_BUCKER_GOES_HERE>/*"
        }
    ]
}
```

