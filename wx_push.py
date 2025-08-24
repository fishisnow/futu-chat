from wxpusher import WxPusher


token = "AT_Fo3ZDapzn5dPbHnxJx1EBgO4HsiZhY3r"

def send_md_message(message):
    WxPusher.send_message(message,
                          content_type=3,
                          uids=['UID_plH4n9fD1cvtwxg2oFcPevOprn3C'],
                          token=token)