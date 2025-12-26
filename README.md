# Reddit Crawler

# Endpoints
1. admin/ <br />
2. users/ <br />
3. api-auth/login/ <br />
4. api-auth/logout/ <br />
5. postsSoup/

## Installation

1. Clone the project files to your computer:

    ```
    git clone https://github.com/furkanonery/reddit-crawler.git
    ```

2. Navigate to the `core` directory:

    ```
    cd  reddit-crawler/core
    ```

3. Install the required dependencies:

    ```
    pip3 install -r requirements.txt
    ```

4. Perform Django migrations to create the database:

    ```
    python3 manage.py migrate
    ```

## Usage

### Starting Celery Worker and Beat

1. Navigate to the `core` directory:

    ```
    cd reddit-crawler/core
    ```

2. To start the Celery Worker, run the following command:

    ```
    celery -A crawler_soup worker --loglevel=info
    ```

3. To start the Celery Beat, run the following command:

    ```
    celery -A crawler_soup beat --loglevel=info
    ```

### Running the Server

1. Navigate to the `core` directory:

    ```
    cd reddit-crawler/core
    ```

2. To run the server, execute the following command:

    ```
    python3 manage.py runserver
    ```

3. Open your browser and visit `http://localhost:8000` to start using Reddit Crawler application.


### Add admin user

1. Navigate to the `core` directory:

    ```
     cd  reddit-crawler/core
    ```

2. To add an admin user, execute the following command:

    ```
    python3 manage.py createsuperuser
    ```
"# reddit-xyz" 
