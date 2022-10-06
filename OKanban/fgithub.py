from click import open_file
import requests, logging
from pathlib import Path

class FGithub:
    '''Gestion du dépot Github
    '''
    url_api_lastest_release= "https://api.github.com/repos/{owner}/{repo}/releases/latest"

    def __init__(self, owner, repo):
        self.repo = {'owner' : owner, 'repo' : repo}
        self.props = self.get_lastest_release()

    def get_lastest_release(self):
        '''Return a json object
        '''
        url = self.url_api_lastest_release.format(**self.repo)
        try:
            response = requests.get(url)
        except Exception as e:
            logging.error(e)
        else:
            return response.json()

    def get_lastest_tag(self):
        if self.props:
            return self.props.get("tag_name")
    def get_lastest_name(self):
        if self.props:
            return self.props.get("name")
    def get_lastest_download_url(self):
        if self.props:
            return {asset.get("name"):asset.get("browser_download_url") for asset in self.props.get('assets',[])}

    def update_from_lastest(self, path = '.'):
        if check_permissions(path):
            for name, url in self.get_lastest_download_url().items():
                logging.info(f"Download {name} from {url}...")
                try:
                    response = requests.get(url)
                except Exception as e:
                    logging.error(e)
                else:
                    file = Path(path) / name
                    logging.info(f"Download done. Store file at {file}")
                    try:
                        with open(file,'wb') as open_file:
                            open_file.write(response.content)
                    except OSError as e:
                        logging.error(e)
                        break
            return True
    
    def check_permissions(self, path):
        pass

if __name__=='__main__':
    from FUTIL.my_logging import *
    my_logging(console_level = DEBUG, logfile_level = INFO, details = True)
    ok = FGithub("FredThx", "OKanbans")
    print(f"lastest Tag : {ok.get_lastest_tag()}")
    print(f"urls : {ok.get_lastest_download_url()}")
    ok.update_from_lastest("c:\\temp\\")