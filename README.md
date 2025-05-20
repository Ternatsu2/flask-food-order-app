# Flask Food Order App - Portfolio Showcase

## Description

This Python Flask web application demonstrates key skills in full-stack development, ideal for freelance projects. It features user authentication, menu & cart management, and a simulated checkout process, ready for customization for various food businesses.

## Prerequisites

*   **Python:** Version 3.11 or higher recommended.
*   **pip:** Python package installer (usually comes with Python).
*   **Virtual Environment Tool:** Python's built-in `venv` module is recommended.

## Key Features

*   **User Authentication:** Secure registration and login system.
*   **Menu Management:** Browse and select food items easily.
*   **Shopping Cart:** Manage items and quantities before ordering.
*   **Simulated Checkout:** Demonstrates payment processing integration.
*   **Order History:** View past orders and their status.
*   **Basic Order Status Tracking:** Track order progress.

## Skills Demonstrated

*   Full-Stack Web Development (Python, Flask, HTML, CSS)
*   Database Integration (SQLAlchemy)
*   RESTful API Design
*   User Authentication and Authorization
*   Template Design (Jinja2, Bootstrap)
*   Testing and Debugging
*   Problem Solving

## Customization Potential

This application is designed to be easily customized for different restaurants or food ordering businesses. Key areas for adaptation include:

*   **Menu Customization:** Easily add, edit, and remove menu items.
*   **Payment Gateway Integration:** Integrate with real payment gateways (e.g., Stripe, PayPal).
*   **Order Status Updates:** Implement real-time order status updates using WebSockets.
*   **UI/UX Enhancements:** Customize the user interface and experience to match specific branding.

## Setup Instructions

1.  **Clone or Download:** Obtain the project source code. If cloning:
    ```bash
    git clone <repository_url>
    # Navigate into the main project directory (the one containing the 'ofos' folder)
    cd <project_root_directory_name> 
    ```

2.  **Create Virtual Environment:** From the project root directory, create a virtual environment (named `venv` here):
    ```bash
    python -m venv venv
    ```

3.  **Activate Virtual Environment:**
    *   **Windows (Command Prompt/PowerShell):**
        ```cmd
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux (Bash/Zsh):**
        ```bash
        source venv/bin/activate
        ```
    *(You should see `(venv)` preceding your command prompt.)*

4.  **Install Dependencies:** Install all required Python packages from the `requirements.txt` file located inside the `ofos` directory:
    ```bash
    pip install -r ofos/requirements.txt
    ```

## Database Setup

*   This application uses **SQLite** for its database. The database file will be automatically created at `ofos/instance/app.db`.
*   **Initialization Method:** The application is configured to automatically create all necessary database tables using `db.create_all()` when it starts (this is handled within `ofos/app/__init__.py`).
*   **Recommendation:** For a clean setup or if you encounter database-related errors, **delete the existing `ofos/instance/app.db` file** before running the application for the first time. The application will generate a fresh database file.
*   **Note on SECRET_KEY:** A default development `SECRET_KEY` is provided in `ofos/config.py`. For production deployment, it is strongly recommended to set a unique, secret key via an environment variable instead.

## Running the Application

1.  **Ensure Virtual Environment is Active:** Check for `(venv)` at the start of your prompt. If not, reactivate it (see Step 3 in Setup).
2.  **Navigate to the `ofos` Directory:** Make sure your terminal's current directory is the `ofos` folder (the one containing `ofos.py`).
    ```bash
    # If you are in the project root directory:
    cd ofos 
    ```
3.  **Run the Application:**
    ```bash
    python ofos.py
    ```
    *(This directly executes the main application script.)*

## Accessing the Application

*   Once the server starts (you should see output indicating it's running, typically on `http://127.0.0.1:5000`), open your web browser.
*   Navigate to: `http://127.0.0.1:5000`

## Basic Usage

1.  **Register/Login:** Create a user account or log in with existing credentials.
2.  **Browse Menu:** Navigate to the "Menu" page to see available items.
3.  **Add to Cart:** Use the "Add" buttons on the menu page to add items to your shopping cart.
4.  **View Cart:** Click the "Cart" link to review items, update quantities, or remove items.
5.  **Checkout:** Proceed to checkout from the cart page (payment is simulated).
6.  **View Order History:** After checkout, navigate to "My Orders" to see your past orders and their status (new orders will show as `RECEIVED`).

## Project Structure Overview

*   `ofos/`: Main application package directory.
    *   `app/`: Contains the core Flask application components.
        *   `__init__.py`: Application factory (`create_app`), initializes extensions.
        *   `models.py`: SQLAlchemy database models (User, Order, MenuItem, OrderItem).
        *   `config.py`: Application configuration class.
        *   `main/`, `auth/`, `order/`: Blueprints containing routes, forms (where applicable), and specific logic.
        *   `templates/`: Jinja2 HTML templates.
        *   `static/`: Static files (CSS, JS - though primarily uses Bootstrap CDN/Flask-Bootstrap).
    *   `instance/`: Instance folder (created automatically), contains the SQLite database (`app.db`).
    *   `tests/`: Contains tests (currently includes basic structure).
    *   `ofos.py`: Main executable script to run the Flask development server.
    *   `requirements.txt`: Python package dependencies.
    *   `.env.example`: Example environment variables file (Note: A `.env` file is **not** required for basic running, as a default `SECRET_KEY` is provided in `config.py`).
    *   `README.md`: This file.
*   `venv/`: Python virtual environment directory (created during setup).

## Technologies Used

*   Python 3.11+
*   Flask
*   Flask-SQLAlchemy
*   Flask-Login
*   Flask-WTF (Forms & CSRF Protection)
*   Flask-Bootstrap (v3 based)
*   Flask-SocketIO
*   SQLite (Database)
*   Jinja2 (Templating)
*   Werkzeug (WSGI utilities, Development Server)
*   python-dotenv (Included in requirements, used for optional `.env` file loading if overriding default config)
