# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /contact_app

# Install pipenv and python-dotenv in one RUN command to minimize the number of layers
RUN pip install --upgrade pip \
    && pip install pipenv python-dotenv

# Copy the Pipfile and Pipfile.lock first to leverage Docker cache
COPY Pipfile Pipfile.lock /contact_app/

# Install dependencies using pipenv and the system flag
RUN pipenv install --deploy --ignore-pipfile --system

# Copy the rest of the application code
COPY . /contact_app/

# Expose the port Django will run on
EXPOSE 8000

# Set environment variables for production (you can customize as needed)
ENV DJANGO_SETTINGS_MODULE=contact_app.settings

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
