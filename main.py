import json
import requests
import bs4
import time
import datetime

config = json.load(open("config.json"))
ua = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_9; en-US) AppleWebKit/537.10 (KHTML, like Gecko) Chrome/53.0.2539.388 Safari/535"
class LastFM:
    def __init__(self, username: str, password: str) -> None:
        self.session = requests.Session()

        self.username = username
        self.password = password
        self.total = 0

        self.listen_path = "https://www.last.fm/player/now-playing"
        self.login_path = "https://www.last.fm/login"
        self.login_post_path = "https://www.last.fm/login"
        self.user_path = "https://www.last.fm/user/%s"
        self.player_scrobble = "https://www.last.fm/player/scrobble"

        self.Login(
            username=self.username,
            password=self.password
        )
    
    def Login(self,username: str, password: str) -> None:
        try:
            r = self.session.get(url=self.login_path)
            soup = bs4.BeautifulSoup(r.text, "html.parser")

            csrf_token = soup.find("input", attrs={"name" : "csrfmiddlewaretoken"}).attrs["value"]

            r = self.session.post(
                url=self.login_post_path,
                data={
                    "next" : "/user/%s" % (username),
                    "username_or_email" : username,
                    "password" : password,
                    "submit" : "",
                    "csrfmiddlewaretoken" : csrf_token
                },
                headers= {
                    "Referer" : self.login_path,
                    "User-Agent" : ua
                }
            )

            if r.status_code == 200:
                print("[LOGIN] as %s" % (username))

            r = self.session.get(url=self.user_path % (username))
            
            csrftoken = self.session.cookies.get("csrftoken")
            self.work(
                artist=config["artist"],
                track=config["track"],
                duration=config["duration"],
                csrfmiddlewaretoken=csrftoken,
            )
        except Exception as e:
            print(e)
            pass
    
    def play_music(
        self,
        artist: str,
        track: str,
        duration: str,
        csrfmiddlewaretoken: str,
    ) -> None:
        try:
            r = self.session.post(
                url=self.listen_path,
                data= {
                    "artist" : artist,
                    "track": track,
                    "duration": duration,
                    "ajax" : "1",
                    "csrfmiddlewaretoken" : csrfmiddlewaretoken
                },
                headers= {
                    "Referer" : self.user_path % (self.username),
                    "User-Agent" : ua
                }
            )

            print("[NOW PLAYING] %s - %s" % (config["artist"], config["track"]))

            end_timestamp = int(datetime.datetime.now().timestamp())
            end_timestamp = end_timestamp + int(duration) 
            self.scrobble(
                timestamp=end_timestamp,
                artist=artist,
                track=track,
                duration=duration,
                csrfmiddlewaretoken=csrfmiddlewaretoken
            )
        except Exception as e:
            print(e)
            pass
    
    def scrobble(
        self,
        timestamp: str,
        artist: str,
        track: str,
        duration: str,
        csrfmiddlewaretoken: str
    ) -> None:
        try:
            
            r = self.session.post(
                url=self.player_scrobble,
                data={
                    "timestamp" : timestamp,
                    "artist" : artist,
                    "track" : track,
                    "duration": duration,
                    "ajax" : "1",
                    "csrfmiddlewaretoken" : csrfmiddlewaretoken
                },
                headers={
                    "Referer" : "https://www.last.fm/home",
                    "User-Agent" : ua
                }
            )
            if r.status_code == 200 and r.json().get("result"):
                self.total = self.total + 1
                print("[SCROBBLE:%d] %s - %s" % (self.total,config["artist"], config["track"]))
        except Exception as e:
            print(e)
    
    def work(
        self,
        artist: str,
        track: str,
        duration: str,
        csrfmiddlewaretoken: str
    ) -> None:
        while 1:
            self.play_music(
                artist=artist,
                track=track,
                duration=duration,
                csrfmiddlewaretoken=csrfmiddlewaretoken
            )
            time.sleep(0.2)







def main():
    LastFM(
        username=config["username"],
        password=config["password"]
    )
    

if __name__ == "__main__":
    main()