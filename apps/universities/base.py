

class Universities:
    def __init__(self, path_to_file=None, headers:list=None):
        with open(path_to_file, 'r', encoding='utf-8') as f:
            table_rows = soup.find_all('tr')

        for table_row in table_rows:
            population = table_row.text.strip()
