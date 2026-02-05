# নতুন এবং স্টেবল ভার্সন ব্যবহার করছি
FROM python:3.11-slim

# যাতে ইন্সটল করার সময় কোনো প্রশ্ন না করে (Yes/No prompt)
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# সিস্টেম প্যাকেজ আপডেট এবং Tesseract ইন্সটল
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# ফাইল কপি করা
COPY . .

# পাইথন লাইব্রেরি ইন্সটল
RUN pip install --no-cache-dir -r requirements.txt

# পোর্ট ওপেন করা
EXPOSE 8501

# অ্যাপ রান করার কমান্ড
ENTRYPOINT ["streamlit", "run", "translator.py", "--server.port=8501", "--server.address=0.0.0.0"]
