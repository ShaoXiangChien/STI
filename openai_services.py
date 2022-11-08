import openai

openai.api_key = "53fb62b1a8a14de2be14289f148e6041"
# your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_base = "https://openaieric.openai.azure.com/"
openai.api_type = 'azure'
openai.api_version = '2022-06-01-preview'


def keyword_extract(doc):
    print('Sending a test completion job')
    start_phrase = doc + "\n關鍵字：\n"
    response = openai.Completion.create(
        engine="text-davinci-002", prompt=start_phrase, max_tokens=50)
    text = response['choices'][0]['text'].replace(
        '\n', '').replace(' .', '.').strip()
    return text.split("\u3000")


def summarize(doc):
    print('Sending a test completion job')
    start_phrase = doc + "\n摘要：\n"
    response = openai.Completion.create(
        engine="text-davinci-002", prompt=start_phrase, max_tokens=500)
    text = response['choices'][0]['text'].replace(
        '\n', '').replace(' .', '.').strip()
    return text
