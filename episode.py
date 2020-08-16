from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import sys

sys.argv

if len(sys.argv) > 1:
    series = ' '.join(sys.argv[1:])
else:
    sys.exit('No series specified')
    # series = 'tt4179452'

response = get('https://www.imdb.com/title/{}/episodes' .format(series))

# Parse the content of the request with BeautifulSoup
page_html = BeautifulSoup(response.text, 'html.parser')

# Select all the episode containers from the season's page
episode_containers = page_html.find_all('h3', itemprop = 'name')
series_name = episode_containers[0].find("a", itemprop="url").text

season_container = page_html.find_all("select", class_="current")[0]
seasons = page_html.find("select", {"id":"bySeason"}).find("option",selected=True).text.strip()

# Initializing the series that the loop will populate
series_episode = []

# For every season in the series-- range depends on the show
for sn in range(1,int(seasons)+1):
    # Request from the server the content of the web page by using get(), and store the server’s response in the variable response
    response = get('https://www.imdb.com/title/{}/episodes?season='.format(series) + str(sn))

    # Parse the content of the request with BeautifulSoup
    page_html = BeautifulSoup(response.text, 'html.parser')

    # Select all the episode containers from the season's page
    episode_containers = page_html.find_all('div', class_ = 'info')

    # For each episode in each season
    for episodes in episode_containers:
            # Get the info of each episode on the page
            season = sn
            episode_number = episodes.meta['content']
            title = episodes.a['title']
            airdate = episodes.find('div', class_='airdate').text.strip()
            rating = episodes.find('span', class_='ipl-rating-star__rating')
            if rating is None:
                rating = 0
            else:
                rating = rating.text
            total_votes = episodes.find('span', class_='ipl-rating-star__total-votes')
            if total_votes is None:
                total_votes = '(0)'
            else:
                total_votes = total_votes.text
            desc = episodes.find('div', class_='item_description').text.strip()
            # Compiling the episode info
            episode_data = [season, episode_number, title, airdate, rating, total_votes, desc]

            # Append the episode info to the complete dataset
            series_episode.append(episode_data)

series_episode = pd.DataFrame(series_episode, columns = ['season', 'episode_number', 'title', 'airdate', 'rating', 'total_votes', 'desc'])
series_episode.head()
def remove_str(votes):
    for r in ((',',''), ('(',''),(')','')):
        votes = votes.replace(*r)
    return votes
series_episode['total_votes'] = series_episode.total_votes.apply(remove_str).astype(int)
series_episode['rating'] = series_episode.rating.astype(float)
series_episode['airdate'] = pd.to_datetime(series_episode.airdate)
series_episode.info()
series_episode.to_csv(r'D:/scripts/'+ series_name + '_Episodes_IMDb_Ratings.csv',index=False)
