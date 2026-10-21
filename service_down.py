from youtube_down_thread import TelechargementWorker

class ServiceDown:
    def __init__(self, url):
        self.url = url

    def start(self):
        if self.__check_text__():
            telechargement = TelechargementWorker(self.url)
            try:
                telechargement.run()
            except Exception as e:
                return str(self.error())
        else:
            raise ValueError("Veiller rentre une url valide")



    @staticmethod
    def error():
        return TelechargementWorker.error

    def __check_text__(self):
        if self.url and self.url.startswith("https://"): return True
        raise ValueError("Veiller rentre une url valide")

    def stop(self):
        tele = TelechargementWorker(self.url)
        if tele.run():
            tele.stop()







if __name__ == "__main__":
    service = ServiceDown("https://www.youtube.com/shorts/bR1eESW6Z2I?t=3&feature=share")

    service.start()

