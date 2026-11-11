import os
import requests
import csv
from datetime import datetime

BASE_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GH_TOKEN")
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_github_data(endpoint):
    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    response.raise_for_status()
    return response.json()

def save_views_clones_data(data, filename):
    # data is a list of {'timestamp': '2026-11-01T00:00:00Z', 'count': X, 'uniques': Y}
    existing = {}
    if os.path.isfile(filename):
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    d = row.get('date')
                    if d:
                        existing[d] = {
                            'date': d,
                            'count': int(row.get('count', 0)),
                            'uniques': int(row.get('uniques', 0))
                        }
        except Exception as e:
            print(f"Warning reading {filename}: {e}")

    for item in data:
        item_date = item['timestamp'][:10]
        existing[item_date] = {
            'date': item_date,
            'count': item['count'],
            'uniques': item['uniques']
        }

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'count', 'uniques'])
        writer.writeheader()
        for d in sorted(existing.keys()):
            writer.writerow(existing[d])

def save_referrers_paths_data(data, filename, data_type):
    today = datetime.now().date().strftime('%Y-%m-%d')
    if not data:
        return

    # Check if already recorded today
    if os.path.isfile(filename):
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('date') == today:
                        return
        except Exception:
            pass

    csv_data = {'date': today}
    padded_data = data[:10] + [{'path': '', 'referrer': '', 'count': '', 'uniques': ''}] * max(0, 10 - len(data))

    for i, item in enumerate(padded_data, 1):
        csv_data[f'{data_type}_{i}'] = item.get('path', '') if data_type == 'path' else item.get('referrer', '')
        csv_data[f'{data_type}_{i}_count'] = item.get('count', '')
        csv_data[f'{data_type}_{i}_uniques'] = item.get('uniques', '')

    file_exists = os.path.isfile(filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_data.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(csv_data)

def get_user_public_repos(username):
    repos = []
    page = 1
    while True:
        try:
            response = get_github_data(f"/users/{username}/repos?per_page=100&page={page}")
            if not response:
                break
            for repo in response:
                repos.append(repo['name'])
            page += 1
        except Exception as e:
            print(f"Error fetching repos for {username}: {e}")
            break
    return sorted(list(set(repos)))

def main():
    with open('github_username.txt', 'r', encoding='utf-8') as file:
        owner = file.read().strip()
        
    repos = get_user_public_repos(owner)
    print(f"Tracking repos for {owner}: {repos}")
    
    for repo in repos:
        print(f"Processing repository: {repo}")
        try:
            views_data = get_github_data(f"/repos/{owner}/{repo}/traffic/views")
            save_views_clones_data(views_data.get('views', []), f'data/github_views/{repo}.csv')
            
            clones_data = get_github_data(f"/repos/{owner}/{repo}/traffic/clones")
            save_views_clones_data(clones_data.get('clones', []), f'data/github_clones/{repo}.csv')
            
            paths_data = get_github_data(f"/repos/{owner}/{repo}/traffic/popular/paths")
            save_referrers_paths_data(paths_data, f'data/github_paths/{repo}.csv', 'path')
            
            referrers_data = get_github_data(f"/repos/{owner}/{repo}/traffic/popular/referrers")
            save_referrers_paths_data(referrers_data, f'data/github_referrers/{repo}.csv', 'ref')
            
        except requests.exceptions.HTTPError as e:
            print(f"Error processing {repo}: {e}")
            continue

if __name__ == "__main__":
    main()
