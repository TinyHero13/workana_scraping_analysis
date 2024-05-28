from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

columns = ['Title', 
           'Price', 
           'Description', 
           'Skills', 
           'Published',
           'Bids']

df = pd.DataFrame(columns=columns)

driver = webdriver.Chrome()

def scroll_to_element_if_not_visible(driver, element):
    if not element.is_displayed():
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
def wait_and_click_element(vire_more_xpath):
    element = None
    while True:
        try:
            element = driver.find_element(By.XPATH, vire_more_xpath)
            if element.is_displayed() and element.is_enabled():
                element.click()
                break
        except:
            time.sleep(4)
    if not element:
        print(f'não achou elemento {vire_more_xpath}')

for page_num in range(1, 50):
    
    url = f'https://www.workana.com/jobs?language=pt&page={page_num}'
    driver.get(url)
    
    if page_num == 1:
        driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click()
        time.sleep(4)
        driver.find_element(By.XPATH, '//*[@id="app"]/div/div[4]/div/div/button/span').click()
        time.sleep(2)
        
    max_projects = len(driver.find_elements(By.XPATH, '//*[@id="projects"]/div'))

            
    for projects_num in range(1, max_projects + 1):
        project_xpath = f'//*[@id="projects"]/div[{projects_num}]'
        
        time.sleep(2)
        projects_element = driver.find_element(By.XPATH, f'{project_xpath}')
        scroll_to_element_if_not_visible(driver, projects_element)
        
        time.sleep(2)
        
        view_more_xpath = f'{project_xpath}/div[2]/div[2]/div/p/a'
        wait_and_click_element(view_more_xpath)
        time.sleep(2)
        
        
         
        title = driver.find_element(By.XPATH, f'{project_xpath}/div[1]/h2/span/a/span').text
        price = driver.find_element(By.XPATH, f'{project_xpath}/div[4]/h4/span/span').text
        description = driver.find_element(By.XPATH, f'{project_xpath}/div[2]/div[2]/div/p/span').text

        try:
            skills = driver.find_element(By.XPATH, f'{project_xpath}/div[2]/div[3]/div').text
        except:
            skills = 'N/A'
        published = driver.find_element(By.XPATH, f'{project_xpath}/div[2]/div[1]/span[1]').text.split('Publicado: ')[-1]
        bids = driver.find_element(By.XPATH, f'{project_xpath}/div[2]/div[1]/span[2]').text.split('Propostas: ')[-1]
        
        new_row = {
            'Title': title,
            'Price': price,
            'Description': description,
            'Skills': skills,
            'Published': published,
            'Bids': bids
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        print(f'Raspagem do conteúdo: {projects_num} da página: {page_num} finalizada!')
    
driver.quit()

df['DescriptionBottom'] =  df['Description'].apply(lambda x: ''.join(x.split('\n\nCategoria: ')[-1]))
df['SubCategory'] =  df['DescriptionBottom'].apply(lambda x: (x.split('Subcategoria: ')[0].split('\n')[0]))
df['Category'] =  df['DescriptionBottom'].apply(lambda x: (x.split('\n',1)[0]))
df['Description'] = df['Description'].apply(lambda x: ' '.join(x.split('\n\nCategoria')[0].split('\n')).strip())
df['Skills'] = df['Skills'].apply(lambda x: ','.join(x.split('\n')))

df.to_csv('workana.csv')