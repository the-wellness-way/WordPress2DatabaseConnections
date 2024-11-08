# WordPress2DatabaseConnections

This AWS Lambda function integrates with **Auth0** for authentication and performs user-related operations on an **Amazon RDS** MySQL database, specifically managing user accounts and authentication credentials for WordPress-like workflows.

## Features

- **User Management**: Creates, deletes, verifies, and updates user records in the RDS database.
- **Password Management**: Allows for password change and email verification workflows.
- **Auth0 Integration**: Retrieves user credentials for Auth0 purposes.
- **Endpoint Support**:
  - `/create_user`: Adds a new user.
  - `/get_user`: Retrieves a user by email.
  - `/delete_user`: Deletes a user by `user_id`.
  - `/change_password`: Updates a user's password.
  - `/verify`: Sets a user's status to verified.

## Prerequisites

1. **Amazon RDS Database**: A MySQL instance with the following database and table structure:
   - **Database**: `tww_users`
   - **Table**: `tww_members`
     - Columns:
       - `id`: `INT`, Auto Increment, Primary Key
       - `member_email`: `VARCHAR(255)`
       - `member_pass`: `VARCHAR(255)`
       - `user_id`: `VARCHAR(100)`
       - `is_active`: `BOOLEAN`

2. **Environment Variables**:
   - `DB_HOST`: Database endpoint for the RDS instance.
   - `DB_USER`: Database username.
   - `DB_PASSWORD`: Database password.
   - `DB_NAME`: Database name (e.g., `tww_users`).

3. **Auth0 Setup**: Set up Auth0 to use this Lambda for user account management by configuring it as a custom database action in Auth0.

## Setup and Deployment

1. **Clone this repository** or download the Lambda code.
2. **Install dependencies** (e.g., `pymysql`) and package them with the Lambda code if necessary.
3. **Deploy the Lambda function** to AWS, ensuring the appropriate permissions to access the RDS instance.

### Environment Variable Configuration

Set the following environment variables in AWS Lambda:

- **DB_HOST**: Hostname of your RDS database.
- **DB_USER**: Username for accessing the database.
- **DB_PASSWORD**: Password for accessing the database.
- **DB_NAME**: Name of the database (`tww_users`).

### IAM Permissions

Ensure that your Lambda function has access to:
- The RDS instance (via VPC and security group configurations).
- CloudWatch Logs for monitoring and debugging.

## Endpoints

### 1. `/create_user`
- **Method**: `POST`
- **Body**: JSON with `email`, `password`, and `user_id`.
- **Response**: Returns `200 OK` with user details on success, `400` if parameters are missing, or `500` if creation fails.

### 2. `/get_user`
- **Method**: `POST`
- **Body**: JSON with `email`.
- **Response**: Returns `200 OK` with user details, including `user_id`, `email`, and `password`.

### 3. `/delete_user`
- **Method**: `DELETE`
- **Query Parameter**: `user_id`.
- **Response**: Returns `200 OK` on success, `404` if user is not found, or `500` on error.

### 4. `/change_password`
- **Method**: `POST`
- **Body**: JSON with `email`, `password`, and `newPassword`.
- **Response**: Returns `200 OK` on success, `401` if the password is incorrect, `404` if the user is not found, or `500` on error.

### 5. `/verify`
- **Method**: `POST`
- **Body**: JSON with `email`.
- **Response**: Returns `200 OK` if the email was verified, or `500` if verification fails.

## Error Handling

All endpoints handle missing parameters and operational errors with JSON responses, including:
- `400` errors for missing or invalid inputs.
- `404` for user-not-found errors.
- `500` for server-related errors, including database connection issues.

## Logging

This function uses AWS CloudWatch for logging. Logs include detailed information about incoming requests and errors for easy debugging.

## Example Request

Here’s an example request to `/create_user`:

```json
POST /create_user
{
  "email": "philiparudy@gmail.com",
  "password": "Tiger2728!",
  "user_id": "wp|500"
}
