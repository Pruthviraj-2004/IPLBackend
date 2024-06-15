# IPLBackend

# Backend Overview

## Introduction

This project is a backend system built with Django, a high-level Python web framework. It handles various functionalities related to user management, match information, and leaderboard data for a predictive play application.

## Key Features

- **User Management**: Registration, login, logout, and password reset functionalities.
- **Match Information**: Handling match details including teams, match dates, times, locations, and player information.
- **Leaderboard Management**: Managing and displaying leaderboards based on user predictions and match results.

## Setup and Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Database Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Create a Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the Server**:
    ```bash
    python manage.py runserver
    ```

## API Endpoints

### User Management

- **Registration**: `POST /ipl2/register_user/`
- **Login**: `POST /ipl2/login_user/`
- **Logout**: `POST /ipl2/logout_user/`
- **Password Reset**: `POST /ipl2/password_reset/`

### Match Information

- **Get All Matches**: `GET /ipl2/fixtures/`
- **Update Match**: `PUT /ipl2/update_match2/<match_id>/`

### Leaderboard

- **Get Leaderboard**: `GET /ipl2/leaderboard2/`
- **User Submissions**: `GET /ipl2/user_submissions/<str:username>/`
- **Register for Leaderboard**: `POST /ipl2/lb_registration/`

## Custom Password Reset

The custom password reset view checks the username and email before sending a password reset email. It restricts certain users from using this feature.

## Admin Interface

The Django admin interface is used to manage the backend data, accessible at `/admin/` (if enabled in settings).

### Custom Admin Filters

In the admin panel, you can filter `SubmissionsInfo` by `predictedteam`, `smatch`, and `username`, with `smatch` being ordered in descending order.

## Contributions

Feel free to fork the repository and submit pull requests. Please ensure your code follows the existing coding style and includes appropriate tests.

## License

This project is licensed under the MIT License.
