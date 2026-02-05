# Python 3.10 image ব্যবহার করা হচ্ছে
FROM python:3.10-slim

# কাজের ফোল্ডার সেট করা
WORKDIR /app

# সিস্টেম আপডেট করা এবং Tesseract OCR ইন্সটল করা (অত্যাবশ্যকীয় ধাপ)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# ফাইলগুলো কপি করা
COPY . .

# Python লাইব্রেরি ইন্সটল করা
RUN pip3 install -r requirements.txt

# পোর্ট ওপেন করা
EXPOSE 8501

# অ্যাপ রান করার কমান্ড
ENTRYPOINT ["streamlit", "run", "translator.py", "--server.port=8501", "--server.address=0.0.0.0"]
