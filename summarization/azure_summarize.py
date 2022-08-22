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

# Example method for summarizing text


def azure_summarize(document):
    global client

    poller = client.begin_analyze_actions(
        document,
        actions=[
            ExtractSummaryAction(max_sentence_count=4)
        ],
    )

    document_results = poller.result()
    summary = ""
    for result in document_results:
        extract_summary_result = result[0]  # first document, first result
        if extract_summary_result.is_error:
            print("...Is an error with code '{}' and message '{}'".format(
                extract_summary_result.code, extract_summary_result.message
            ))
        else:
            text = " ".join(
                [sentence.text for sentence in extract_summary_result.sentences])
            print("Summary extracted: \n{}".format(text))
            summary += text
    return summary


# sample_extractive_summarization(client)
