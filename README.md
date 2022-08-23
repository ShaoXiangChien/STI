# STI

## Environment Setup
1. [install anaconda](https://medium.com/python4u/anaconda%E4%BB%8B%E7%B4%B9%E5%8F%8A%E5%AE%89%E8%A3%9D%E6%95%99%E5%AD%B8-f7dae6454ab6)
2. Create a new environment called  
`conda create --name STI python=3.7`
3. Activate the environment  
`conda activate STI`
4. Install all the packages in the requirement  
`conda install --file requirements.txt`

## Streamlit App Usage
To launch the web app, in terminal:
```
streamlit run main.py
```
The generated URL is the link to the app.

## google_search_api Usage
- for special keywords:
  ```
  {
    result_type: 'organic_results',
    pagination: False
   }
  ```