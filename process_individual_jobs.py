# -*- coding: utf-8 -*-
"""
process individual jobs and extract key job info
"""
import pandas as pd
import os
from lxml import etree

html_files = [x for x in os.listdir('webpage_data') if x[-5:] == '.html']
job_df = pd.DataFrame(columns=['job_id', 'title', 'company', 'company_url', 'location', 'seniority', 'full_time', 'company_size', 'industry', 'recruitment_status', 'job_description'])

for html_file in html_files:
    print(html_file)
    job_id = html_file.split('.')[0]
    job_dict = {'job_id': job_id}
    with open(os.path.join('webpage_data', html_file), 'r', encoding="utf-8") as f:
        tree = etree.HTML(f.read().encode("utf-8"))
        # job title
        title_xpath = "//div[@class='p5']/h1"
        title_element = tree.xpath(title_xpath)
        job_dict['title'] = title_element[0].text.strip()
        # company name and url
        company_xpath = "//span[@class='jobs-unified-top-card__company-name']/a"
        company_element = tree.xpath(company_xpath)
        job_dict['company_url'] = f"https://www.linkedin.com{company_element[0].get('href')}"
        job_dict['company'] = company_element[0].text.strip()
        # job location
        location_xpath = "//span[@class='jobs-unified-top-card__bullet']"
        location_element = tree.xpath(location_xpath)
        job_dict['location'] = location_element[0].text.strip()
        # job insights
        insight_xpath = "//li[@class='jobs-unified-top-card__job-insight']/span/text()"
        insight_elements = tree.xpath(insight_xpath)
        insight_texts = [x for x in insight_elements if len(x.strip()) > 2]
        if len(insight_texts) == 3:
            print(insight_texts) #['Full-time · Mid-Senior level', '10,001+ employees · Financial Services', 'Actively recruiting']
            job_dict['full_time'] = insight_texts[0].split('·')[0].strip()
            try:
                job_dict['seniority'] = insight_texts[0].split('·')[1].strip()
            except IndexError:
                job_dict['seniority'] = ''
            job_dict['company_size'] = insight_texts[1].split('·')[0].strip()
            job_dict['industry'] = insight_texts[1].split('·')[1].strip()
            job_dict['recruitment_status'] = insight_texts[2]
        else:
            job_dict['full_time'] = ''
            job_dict['seniority'] = ''
            job_dict['company_size'] = ''
            job_dict['industry'] = ''
            job_dict['recruitment_status'] = ''
        # job description
        job_about_xpath = "//h2[@class='mt5 t-20 t-bold mb4']/../span"
        job_about_element = tree.xpath(job_about_xpath)
        job_about_text = ''.join(job_about_element[0].itertext())
        job_dict['job_description'] = job_about_text.strip()

        job_df = job_df.append(job_dict, ignore_index=True)
job_df.to_csv('job_infos_v1.csv', index=False)
