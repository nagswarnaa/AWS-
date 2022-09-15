This is a web based file sharing tool which supports  sharing with multiple users. 

The user logs into the website and gets a file upload screen. The user chooses the file from local storage and also enters a number of email addresses (up to 5). Once the user hits upload, the file is stored in S3. Also, the link to the file is emailed to the provided email addresses.

All the files that are uploaded will be stored in the AWS S3.

I have used AWS EC2 to host this application and AWS S3 to store the files uploaded and AWS RDS to store the details of the file uploads and AWS SNS to notify the users about file upload status 

