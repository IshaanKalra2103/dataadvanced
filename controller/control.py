import os
import glob
import time
import torch
import smtplib
import tempfile
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from multiprocessing import Pool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GPU Check
def is_gpu_available():
    return torch.cuda.is_available()

# Function to process a single PDF
def process_single_pdf(pdf_path):
    with tempfile.TemporaryDirectory() as output_dir:
        try:
            start_time = time.time()
            command = f'PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0 marker_single "{pdf_path}" "{output_dir}"'
            subprocess.run(command, shell=True, check=True, env=dict(os.environ))
            markdown_files = glob.glob(os.path.join(output_dir, '**', '*.md'), recursive=True)
            if markdown_files:
                with open(markdown_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                end_time = time.time()
                print(f"Processed {pdf_path} in {end_time - start_time:.2f} seconds")
                return content
            else:
                raise FileNotFoundError(f"No markdown file found for {pdf_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {pdf_path}: {e}")
            return None

# Function to process a batch of PDFs
def process_batch(pdf_paths):
    results = []
    for pdf in pdf_paths:
        result = process_single_pdf(pdf)
        results.append(result)
    return results

# Batch processing
def process_pdfs_in_batches(pdf_paths, batch_size=5):
    for i in range(0, len(pdf_paths), batch_size):
        batch = pdf_paths[i:i + batch_size]
        print(f"Processing batch: {batch}")
        process_batch(batch)

# Email notification
def send_email_notification(receiver_email, message_body):
    sender_email = os.getenv('EMAIL_USER')
    sender_password = os.getenv('EMAIL_PASS')
    subject = "PDF Processing Complete"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"Email sent to {receiver_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main execution
def main(pdf_dir, email):
    # Get all PDF files from the directory
    pdf_paths = glob.glob(os.path.join(pdf_dir, '*.pdf'))

    # Check for GPU
    if is_gpu_available():
        print("GPU is available. Processing with GPU support.")
    else:
        print("No GPU available. Proceeding with CPU.")

    # Process PDFs in batches
    batch_size = 5  # Set your batch size
    process_pdfs_in_batches(pdf_paths, batch_size)

    # After all processing, send an email notification
    send_email_notification(email, "All PDF files have been processed successfully.")

if __name__ == "__main__":
    pdf_directory = "/Users/ishaankalra/Research-CGS/Projects/Data Extraction/papers"  # Update with the actual path
    user_email = "kalraishaan907@gmail.com"  # Update with the actual email address
    main(pdf_directory, user_email)