import re
import os
import urllib
import random
from linebot.models import *
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError


app = Flask(__name__)

Channel_Access_Token = ''
line_bot_api    = LineBotApi(Channel_Access_Token)
Channel_Secret  = ''
handler = WebhookHandler(Channel_Secret)

# handle request from "/callback" 
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body      = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# handle text message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text

    try:
        img_search = {'tbm': 'isch', 'q': msg}
        query = urllib.parse.urlencode(img_search)
        base  = "https://www.google.com/search?"
        url   = str(base+query)
        
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        
        res  = urllib.request.Request(url, headers=headers)
        con  = urllib.request.urlopen(res)
        data = con.read()

        pattern = '"(https://encrypted-tbn0.gstatic.com[\S]*)"'
        img_list = []

        for match in re.finditer(pattern, str(data, "utf-8")):
            if len(match.group(1)) < 150:
                img_list.append(match.group(1))

        random_img_list = random.sample(img_list, k=5)

        img_template = ImageCarouselTemplate(
            columns=[ImageCarouselColumn(image_url=url, action=URIAction(label=f"image{i}", uri=url))
            for i, url in enumerate(random_img_list)]
        )

        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text=f"ImageCarousel",
                template=img_template
            )
        )

        # 回覆單一圖片
        # random_img_url = img_list[random.randint(0, len(img_list)+1)]

        # message = ImageSendMessage(
        #     original_content_url = random_img_url,
        #     preview_image_url    = random_img_url
        #     )
        # line_bot_api.reply_message(event.reply_token, message)

    # 回傳使用者訊息
    except:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )
        pass


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
