
var AWS = require('aws-sdk');
var lambda = new AWS.Lambda();
exports.handler = function(event, context, callback) {

    var key = event.Records[0].s3.object.key;
    var bucket = event.Records[0].s3.bucket.name
    var functionName = key.substring(0, key.length-4);

    console.log("uploaded to lambda function: " + functionName);

    var params = {
        FunctionName: functionName,
        S3Key: key,
        S3Bucket: bucket
        };

    // Update the lambda function
    lambda.updateFunctionCode(params, function(err, data) {
                if (err) {
                    console.log("Operation failed.");
                    console.log(err, err.stack);
                    context.fail(err);
                } else {
                    console.log("Operation successful.");
                    console.log(data);
                    context.succeed(data);
                }
            });
