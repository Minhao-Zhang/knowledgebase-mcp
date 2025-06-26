# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies using Tsinghua mirror
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy the rest of the application code into the container
COPY . .

# Expose the port the application runs on
EXPOSE 8002

# Command to run the application
CMD ["fastmcp", "run", "main.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8002"]
