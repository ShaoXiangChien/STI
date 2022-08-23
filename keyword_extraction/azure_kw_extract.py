from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractSummaryAction
)
key = "4d9491464469449187508862d7ae45c3"
endpoint = "https://languageserviceforsti.cognitiveservices.azure.com/"


# Authenticate the client using your key and endpoint

def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=ta_credential,
        default_language="zh")
    return text_analytics_client


client = authenticate_client()


def azure_kw_extract(df):
    global client
    documents = df['full_text'].to_list()[:10]
    response = client.extract_key_phrases(documents, language="zh")
    result = [doc for doc in response if not doc.is_error]
    return result[0].key_phrases[:20]
# sample_extractive_summarization(client)
