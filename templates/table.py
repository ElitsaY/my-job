import pandas as pd
import sys


def generate_table_rows(filename: str) -> str:
    df = pd.read_csv(filename)
    for _, row in df.iterrows():
        yield f'''
        <tr>
            <td class="company" data-label="Company"><a href="{row['company']}"><strong>{row['job_title']}</strong></a></td>
            <td data-label="Position">{row['job_title']}</td>
            <td data-label="Location">{row['location']}</td>
            <td class="apply-cell" data-label="Posting"><a href="{row['job_link']}" target="_blank" rel="noopener noreferrer"><img src="https://i.imgur.com/JpkfjIq.png" alt="Apply" class="apply-btn"/></a></td>
        </tr>
        '''

# find ###TABLE_ROWS### in index.html and replace it with the generated rows
def update_html_table(html_path: str, datasource_path: str):
    with open('./templates/template.html', 'r') as file:
        html_content = file.read()
        table_rows = ''.join(generate_table_rows(datasource_path))
        updated_content = html_content.replace('###TABLE_ROWS###', table_rows)
        with open(html_path, 'w') as wr_file:
            wr_file.write(updated_content)


if __name__ == "__main__":
    if len(sys.argv) != 3 and sys.argv[1].endswith('.html') and sys.argv[2].endswith('.csv'):
        print("Usage: python table.py <path_to_index.html> <path_to_datasource.csv>")
        sys.exit(1)
    update_html_table(sys.argv[1], sys.argv[2])