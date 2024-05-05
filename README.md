# S2F web

This is a queue system that takes fasta files and optional `protein-GO term`
association files and runs the S2F pipeline on a server.

## Architecture

The front end, queue manager and mailer runs in a single Django application.

A "polling" backend (or API client for the queue manager) runs using a cron job
on any server that contains a proper S2F installation. It requires to simply 
set up the appropriate environment variables to upload the result files to an
Azure Blob Storage server, as well as the OAuth credentials of the client. 
These credentials can be generated using super user in the Django application.
