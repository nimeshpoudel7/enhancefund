import pdfplumber
import pandas as pd
import re
from datetime import datetime


def load_and_preprocess_data(pdf_file):
    """
    Load and preprocess PDF file content.
    """
    text = extract_text_from_pdf(pdf_file)

    if 'scotia' in text.lower():
        df = parse_scotia_statement(text)
    elif 'RBC®' in text:
        df = parse_rbc_statement(text)
    else:
        raise ValueError("No valid statement found in the PDF")

    if df.empty:
        raise ValueError("No valid transaction data found in the PDF")

    df['month'] = df['transaction_date'].dt.month
    df['day_of_week'] = df['transaction_date'].dt.dayofweek

    features = extract_features(df)

    statement_start_date = df['transaction_date'].min()
    statement_end_date = df['transaction_date'].max()

    return features, statement_start_date, statement_end_date


def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file.
    """
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_features(df):
    """
    Extract features from transaction DataFrame.
    """
    features = pd.DataFrame()
    features['total_spending'] = [abs(df[df['amount'] < 0]['amount'].sum())]
    features['average_transaction'] = [df['amount'].abs().mean()]
    features['transaction_frequency'] = [len(df) / (df['transaction_date'].max() - df['transaction_date'].min()).days]
    features['large_purchase_frequency'] = [(df['amount'] < -100).mean()]
    features['recurring_transactions'] = [detect_recurring_transactions(df)]
    features['payment_consistency'] = [calculate_payment_consistency(df)]
    features['credit_utilization'] = [calculate_credit_utilization(df)]
    return features


def extract_text_from_pdf(pdf_file):
    pdf_reader = pdfplumber.open(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    # print(f"Extracted text (first 500 characters): {text}")
    return text


def parse_date(date_string):
    date_formats = ['%b %d', '%b %d/%y', '%d %b', '%d-%b']
    for fmt in date_formats:
        try:
            date = datetime.strptime(date_string, fmt)
            if date.year == 1900:
                date = date.replace(year=datetime.now().year)
            return date
        except ValueError:
            pass
    return None


def clean_extracted_text(text):
    # Insert spaces between dates (e.g., MAY 27 MAY 28)
    text = re.sub(r'(\w{3})(\d{2})', r'\1 \2', text)

    # Insert spaces between amounts (e.g., $122.39)
    text = re.sub(r'(\d)([A-Z])', r'\1 \2', text)  # Add space between digits and letters

    # Insert spaces between letters and numbers (e.g., BESTBUY#926)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)

    # Insert spaces between numbers and letters (e.g., 926MISSISSAUGA)
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)

    # Insert spaces before and after special characters like #
    text = re.sub(r'(#)', r' \1 ', text)

    # Insert spaces between uppercase letters that are joined together
    text = re.sub(r'([A-Z])([A-Z])', r'\1 \2', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    return text


def parse_scotia_statement(text):
    transactions = []
    lines = text.split('\n')

    scotia_pattern = r'(\d{3})\s+(\w{3}\s\d{1,2})\s+(\w{3}\s\d{1,2})\s+(.*?)\s+([-]?\d+\.\d{2}-?)'

    for line in lines:
        match = re.search(scotia_pattern, line)
        if match:
            ref_num = match.group(1)
            trans_date = parse_date(match.group(2))
            post_date = parse_date(match.group(3))
            description = match.group(4).strip()
            amount_str = match.group(5)

            if amount_str.endswith('-'):
                amount = -float(amount_str.rstrip('-'))
            else:
                amount = float(amount_str)

            if trans_date and post_date:
                transactions.append({
                    'ref_num': ref_num,
                    'transaction_date': trans_date,
                    'post_date': post_date,
                    'description': description,
                    'amount': amount
                })

    if not transactions:
        return


    df = pd.DataFrame(transactions)

    if not df.empty:
        # Extract the month from the transaction dates
        df['statement_month'] = df['transaction_date'].dt.strftime('%B')  # Month name (e.g., January)
    print(df)
    return df


def parse_daterbc(date_str):
    # Placeholder for the date parsing function
    # Ensure this function is defined correctly to parse the dates from the format you have
    return pd.to_datetime(date_str, format='%b %d', errors='coerce')


def parse_rbc_statement(text):
    transactions = []

    # Clean the text by adding spaces where appropriate
    text = re.sub(r'([A-Z]{3}\d{2})', r' \1', text)  # Add space between dates like 'MAY27' -> 'MAY 27'
    text = re.sub(r'(\d)([A-Z])', r'\1 \2', text)  # Add space between digits and letters
    text = re.sub(r'(\$)(\d+)', r'\1 \2', text)  # Add space between dollar sign and amounts
    text = re.sub(r'([A-Z]{2,})(\d{2})', r'\1 \2', text)  # Add space between capital letters and digits
    text = re.sub(r'(-?\$)(\d+)', r'\1 \2', text)  # Ensure correct spacing around the dollar amounts

    # Updated RBC regex pattern to capture transaction details including negative amounts
    rbc_pattern = r'([A-Z]{3} \d{2})\s+([A-Z]{3} \d{2})\s+(.*?)\s+(-?\$\s*\d+\.\d{2})'

    lines = text.split('\n')
    print(f"Number of lines: {len(lines)}")

    for line in lines:
        print(f"Processing line: {line}")  # Debugging each line
        match = re.search(rbc_pattern, line)
        if match:
            trans_date = parse_daterbc(match.group(1))  # Parse the transaction date
            post_date = parse_daterbc(match.group(2))  # Parse the posting date
            description = match.group(3).strip()  # Extract the description

            amount_str = match.group(4)  # This should now capture negative amounts as well
            print(f"Raw Amount: {amount_str}")  # Debugging print statement

            # Clean up the amount string before conversion
            amount_str = amount_str.replace('$', '').replace(',', '').replace(' ', '').strip()
            print(f"Cleaned Amount String: '{amount_str}'")  # Debugging print statement

            try:
                # Convert to float directly, considering negative sign if present
                amount = float(amount_str)
                print(f"Converted Amount: {amount}")  # Check the converted amount
            except ValueError:
                continue  # Skip to the next line if conversion fails

            if trans_date and post_date:
                transactions.append({
                    'transaction_date': trans_date,
                    'post_date': post_date,
                    'description': description,
                    'amount': amount
                })

    if not transactions:
        return


    df = pd.DataFrame(transactions)

    if not df.empty:
        # Extract the month from the transaction dates
        df['statement_month'] = df['transaction_date'].dt.strftime('%B')  # Month name (e.g., January)
    print(df['amount'])
    return df


def parse_daterbc(date_string):
    """Parse date string in formats like 'MAY 27', 'JUN 03', etc."""
    date_formats = ['%b %d']
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).replace(year=datetime.now().year)
        except ValueError:
            continue
    return None


def load_and_preprocess_data(pdf_file):
    text = extract_text_from_pdf(pdf_file)

    if 'scotia' in text.lower():
        df = parse_scotia_statement(text)
    elif 'RBC®' in text:
        df = parse_rbc_statement(text)

    else:
        raise FileExistsError("No Scotia statement found.")
        return

    if df.empty:
        raise ValueError("No valid transaction data found in the PDF")

    df['month'] = df['transaction_date'].dt.month
    df['day_of_week'] = df['transaction_date'].dt.dayofweek

    # Extract features as before
    features = extract_features(df)
    print(features)
    # Get the full statement date range (min and max transaction dates)
    statement_start_date = df['transaction_date'].min()
    statement_end_date = df['transaction_date'].max()

    # Drop the date columns to ensure only numerical data is passed to the model
    # features = features.drop(columns=['statement_start_date', 'statement_end_date'], errors='ignore')

    return features, statement_start_date, statement_end_date


def extract_features(df):
    features = pd.DataFrame()
    features['total_spending'] = [abs(df[df['amount'] < 0]['amount'].sum())]
    features['average_transaction'] = [df['amount'].abs().mean()]
    features['transaction_frequency'] = [len(df) / (df['transaction_date'].max() - df['transaction_date'].min()).days]
    features['large_purchase_frequency'] = [(df['amount'] < -100).mean()]

    features['recurring_transactions'] = [detect_recurring_transactions(df)]
    features['payment_consistency'] = [calculate_payment_consistency(df)]
    features['credit_utilization'] = [calculate_credit_utilization(df)]

    return features


def detect_recurring_transactions(df):
    expenses = df[df['amount'] < 0].groupby('description')
    recurring = expenses.filter(lambda x: len(x) > 2 and x['transaction_date'].diff().dt.days.std() < 5)
    return len(recurring) / len(df)


def calculate_payment_consistency(df):
    payments = df[df['amount'] > 0]
    if len(payments) < 2:
        return 0
    payment_intervals = payments['transaction_date'].diff().dt.days
    return 1 / (1 + payment_intervals.std())


def calculate_credit_utilization(df):
    total_credit_used = abs(df[df['amount'] < 0]['amount'].sum())
    assumed_credit_limit = 1000  # Adjust this based on your requirement
    return min(total_credit_used / assumed_credit_limit, 1)




def calculate_credit_score(model, scaler, features):

    # Ensure features is a 2D array for a single sample
    features_reshaped = features.reshape(1, -1) if features.ndim == 1 else features

    features_scaled = scaler.transform(features_reshaped)
    probabilities = model.predict_proba(features_scaled)

    # Check for the number of classes
    if probabilities.shape[1] > 1:
        probability = probabilities[0][1]  # Positive class
    else:
        probability = probabilities[0][0]  # Only one class present

    credit_score = int(probability * 1000)
    return credit_score




def calculate_risk_score(features):
    risk_score = 0

    # Frequency of large purchases (e.g., > 10% of income) in the last month
    if features['large_purchase_frequency'].values[0] > 0.1:  # 10% threshold
        risk_score += 20

    # Number of transactions per day (adjusted for 1-month period)
    if features['transaction_frequency'].values[0] > 2:  # More than 2 transactions per day
        risk_score += 15

    # Credit utilization in the last month
    if features['credit_utilization'].values[0] > 0.5:  # 50% or more utilization
        risk_score += 25

    # Payment consistency (e.g., paying bills on time)
    if features['payment_consistency'].values[0] < 0.5:  # Less than 50% consistency
        risk_score += 20

    # Low recurring transactions (e.g., utilities, subscriptions)
    if features['recurring_transactions'].values[0] < 0.2:  # Less than 20% of transactions are recurring
        risk_score += 10

    return min(risk_score, 100)
