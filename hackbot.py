#!/usr/bin/python3
import time
import subprocess
import telepot
import os
import re
import json
import datetime
import requests
import threading
import wikipedia
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import youtube_dl


def handle(msg):
    chat_id = msg['chat']['id']
    command = msg.get('text', "")

    print("Got Command : %s" % command)
    bot.sendMessage(chat_id, '😁 Welcome to -+ HackBot v1.2 +- (https://goo.gl/mxQ4Sv) ✔')

    # ---------- HELP ----------
    if command.startswith('help') or command.startswith('/start'):
        bot.sendMessage(chat_id, '😊 HELP MENU:')
        bot.sendMessage(chat_id, '1. Run built‑in tools : nmap -sV site.com')
        bot.sendMessage(chat_id, '2. Folder + Command : tool foldername python script.py')
        bot.sendMessage(chat_id, '3. BTC Price : btc usd')
        bot.sendMessage(chat_id, '4. HackerOne bugs : h1bugs')
        bot.sendMessage(chat_id, '5. Tweets search : tweet bugbounty 5')
        bot.sendMessage(chat_id, '6. HackerOne report : #152407')
        bot.sendMessage(chat_id, '7. Program‑specific H1 bugs : h1bugs programname')
        bot.sendMessage(chat_id, '8. Auto H1 notify : notifyh1')
        bot.sendMessage(chat_id, '9. Wikipedia search : wiki topic')
        bot.sendMessage(chat_id, '10. YouTube → mp3 : yt music')
        bot.sendMessage(chat_id, '11. Motivate every hour : motivateme')
        return

    # ---------- AUTO H1 NOTIFY ----------
    def notifyh1():
        site = requests.get(
            'https://hackerone.com/hacktivity.json?sort_type=latest_disclosable_activity_at&filter=type%3Apublic'
        )
        json_data = site.json()
        rep_id = json_data['reports'][0]['id']
        rep_str = str(rep_id)

        if os.path.exists('latest.txt'):
            with open('latest.txt', 'r') as rmf:
                old = rmf.read().strip()
        else:
            old = ""

        if old != rep_str:
            with open('latest.txt', 'w') as wmf:
                wmf.write(rep_str)
            bot.sendMessage(chat_id, "🐞 New Bug Disclosed on H1 🐞")
            bot.sendMessage(chat_id, "Title: " + json_data['reports'][0]['title'])

        bot.sendMessage(chat_id, "https://hackerone.com" + json_data['reports'][0]['url'])
        threading.Timer(300, notifyh1).start()

    if command.lower().startswith('notifyh1'):
        notifyh1()
        return

    # ---------- TOOL ----------
    if command.lower().startswith('tool'):
        words = command.split()
        folder = words[1]
        cmd = " ".join(words[2:])
        directory = '/root/Desktop/pentest/' + folder

        bot.sendMessage(chat_id, "💼 Path: " + directory)

        if os.path.isdir(directory):
            os.chdir(directory)
            bot.sendMessage(chat_id, "📁 Changed directory: " + directory)
            bot.sendMessage(chat_id, "🐍 " + cmd)
            bot.sendMessage(chat_id, "💻 Running...")

            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                bot.sendMessage(chat_id, output.decode('utf-8'))
            except Exception as e:
                bot.sendMessage(chat_id, "Error: " + str(e))
        else:
            bot.sendMessage(chat_id, "Folder not found!")
        return

    # ---------- WIKIPEDIA ----------
    if command.lower().startswith('wiki'):
        try:
            query = command[5:]
            result = wikipedia.summary(query, sentences=10)
            page = wikipedia.page(query).url
            bot.sendMessage(chat_id, result + "\n" + page)
        except Exception as e:
            bot.sendMessage(chat_id, "Error: " + str(e))
        return

    # ---------- BTC PRICE ----------
    if command.lower().startswith('btc'):
        currency = command[4:]
        url = "https://www.google.com/search?q=bitcoin+to+" + currency
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req).read().decode("utf-8")

        match = re.search("1 Bitcoin = ([0-9,\.]+)", data)
        if match:
            bot.sendMessage(chat_id, f"1 BTC = {match.group(1)} {currency}")
        return

    # ---------- H1 BUGS ----------
    if command.lower().startswith('h1bugs'):
        program = command[7:].strip()

        bot.sendMessage(chat_id, "🚀 Loading HackerOne bugs...")

        if program:
            url = f'https://hackerone.com/hacktivity.json?filter=type%3Apublic%20to%3A{program}'
        else:
            url = 'https://hackerone.com/hacktivity.json?sort_type=latest_disclosable_activity_at&filter=type%3Apublic'

        js = requests.get(url).json()

        for i in range(10):
            try:
                title = js['reports'][i]['title']
                link = "https://hackerone.com" + js['reports'][i]['url']
                bot.sendMessage(chat_id, "Title: " + title)
                bot.sendMessage(chat_id, link)
            except:
                pass
        return

    # ---------- H1 REPORT ----------
    if command.startswith('#'):
        repnum = command[1:]
        bot.sendMessage(chat_id, "🚀 Loading report...")
        js = requests.get(f'https://hackerone.com/reports/{repnum}.json').json()

        title = js['title']
        reporter = js['reporter']['username']
        state = js['readable_substate']
        url = f"https://hackerone.com/reports/{repnum}"

        bot.sendMessage(chat_id,
                        f"(#{repnum}) {title} — by {reporter} ({state})\n{url}")

        if js.get("has_bounty?"):
            bot.sendMessage(chat_id, "Bounty: " + js["formatted_bounty"])

        bot.sendMessage(chat_id, js["vulnerability_information"])
        return

    # ---------- YOUTUBE TO MP3 ----------
    if command.lower().startswith('yt'):
        search = command[3:]
        html = urlopen("https://www.youtube.com/results?search_query=" + search).read()
        soup = BeautifulSoup(html, "html.parser")
        vid = soup.find("a", {"class": "yt-uix-tile-link"})

        link = "https://www.youtube.com" + vid['href']
        title = vid['title']
        short = title[:12]

        bot.sendMessage(chat_id, title + "\n" + link)

        options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }]
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([link])

        for f in os.listdir('.'):
            if short in f and f.endswith(".mp3"):
                bot.sendAudio(chat_id, audio=open(f, 'rb'))
                os.remove(f)
        return

    # ---------- DEFAULT = RUN SYSTEM COMMAND ----------
    bot.sendMessage(chat_id, "😈 [+] Got Command")
    bot.sendMessage(chat_id, command)
    bot.sendMessage(chat_id, "💻 Running...")

    try:
        out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        bot.sendMessage(chat_id, out.decode())
    except Exception as e:
        bot.sendMessage(chat_id, "Error: " + str(e))


# ---------- BOT START ----------
api = open('api.txt', 'r').read().strip()
bot = telepot.Bot(api)
bot.message_loop(handle)

print("[+] Server is Listening [+]")

while True:
    time.sleep(10)				bot.sendMessage(chat_id,'11. Get motivated every hour. Just text -> motivateme')
				return 0
			#end welcome
		
			#automatic hackerone notifier
		def notifyh1():
			site = requests.get('https://hackerone.com/hacktivity.json?sort_type=latest_disclosable_activity_at&filter=type%3Apublic')
			json_data = json.loads(site.text)
			rep_id = json_data['reports'][0]['id']
			rep_str = str(rep_id)
			with open('latest.txt', 'r') as rmf:
				data = rmf.read().replace('\n', '')
			if data != rep_str:
				with open('latest.txt', 'w') as wmf:
					wmf.write("%s" % rep_str)
				bot.sendMessage(chat_id,"\xF0\x9F\x90\x9B New Bug Disclosed on H1 \xF0\x9F\x90\x9B")
				bot.sendMessage(chat_id,"Title: "+json_data['reports'][0]['title']+" ("+json_data['reports'][0]['readable_substate']+")")
			bot.sendMessage(chat_id,"https://hackerone.com"+json_data['reports'][0]['url'])
			print(time.ctime())
			threading.Timer(300, notifyh1).start()
		if command.startswith('notifyh1') or command.startswith('Notifyh1'):
			notifyh1()
			return 0
					#end automatic hackerone notifer
						
					#tool
		elif command.startswith('tool') or command.startswith('Tool'):
			words = command.split()
			mm=words[1]
			cmd=words[2]+' '+words[3]
			final=words[2:]
			print map(str,final)
			makeitastring = ' '.join(map(str, final))
			print makeitastring
			directory='/root/Desktop/pentest/'+str(mm)
			bot.sendMessage(chat_id,"\xF0\x9F\x92\xBC your Path: "+str(directory))
			
			if os.path.isdir(directory):
				print "PATH IS OK"
				try:
					os.chdir(directory)
					bot.sendMessage(chat_id,"\xF0\x9F\x93\x81 Changing Directory to: "+str(directory))
					print "OK"
					bot.sendMessage(chat_id,'\xF0\x9F\x90\x8D '+str(makeitastring))
					bot.sendMessage(chat_id,'\xF0\x9F\x92\xBB  [-] Wait.....[-]')
					pp=subprocess.check_output(makeitastring,shell=True)
					bot.sendMessage(chat_id,pp)
				except ValueError as ex:
					bot.sendMessage(ex,'Something')
			else:
				bot.sendMessage(chat_id,'Error : please check your folder path')
				bot.sendMessage(chat_id,'Make sure you folder at /root/Desktop/pentest/')
			return 0
		#end tool
				
				#wiki starts
		elif command.startswith('wiki') or command.startswith('Wiki'):
			try:
				makesplit=command[5:]
				print makesplit
				wiksearch = wikipedia.summary(makesplit,sentences=10)
				bot.sendMessage(chat_id,wiksearch+'\n'+wikipedia.page(makesplit).url)
			except Exception as e:
				bot.sendMessage(chat_id,'Error :'+str(e))
			return 0
					
	#wiki ends
	
		#btc price
		elif command.startswith('btc') or command.startswith('Btc'):
				arg1=command[4:]
				print arg1
				url= "https://www.google.co.in/search?q=bitcoin+to+"+arg1
				req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
				con = urllib2.urlopen( req )
				Text=con.read()
				position=re.search("1 Bitcoin =",Text)
				res = float(Text[position.end():position.end()+9])
				axx = '1 BTC : '+str(res)+' '+arg1
				bot.sendMessage(chat_id,str(axx))
				return 0
		#end btc price
	
		#h1 disclosed report
		elif command.startswith('h1bugs') or command.startswith('H1bugs'):
			program=command[7:]
			#specific program
			if program:
				bot.sendMessage(chat_id,'\xF0\x9F\x9A\x80  Loading HackerOne Disclosed Bugs!  \xF0\x9F\x9A\x80')
				bot.sendMessage(chat_id, 'Program: '+program)
				site = requests.get('https://hackerone.com/hacktivity.json?filter=type%3Apublic%20to%3A'+program)
				json_data = json.loads(site.text)
				for i in range(10):
					try:
						title = "Title : "+json_data['reports'][i]['title']
						url = json_data['reports'][i]['url']
						urls = "Report at : https://hackerone.com/"+url
						bot.sendMessage(chat_id,title)
						bot.sendMessage(chat_id,urls)
						print "\n"
					except KeyError:
						pass
	
		#common hacktivity
			else:
				bot.sendMessage(chat_id,'\xF0\x9F\x9A\x80  Loading HackerOne Disclosed Bugs!  \xF0\x9F\x9A\x80')
				site = requests.get('https://hackerone.com/hacktivity.json?sort_type=latest_disclosable_activity_at&filter=type%3Apublic')
				json_data = json.loads(site.text)
				for i in range(10):
					try:
						title = "Title : "+json_data['reports'][i]['title']
						url = json_data['reports'][i]['url']
						urls = "Report at : https://hackerone.com/"+url
						bot.sendMessage(chat_id,title)
						bot.sendMessage(chat_id,urls)
						print "\n"
					except KeyError:
						pass
			return 0
		#end h1 disclosed report.
	
		#twitter search 
		elif command.startswith('tweet') or command.startswith('Tweet'):
			twords=command.split()
			tname=twords[1]
			print tname
			timetweets=twords[2]
			print timetweets
			turl = "https://twitter.com/search?q="+tname+"&src=typd&lang=en"
			print turl
			bot.sendMessage(chat_id,'\xF0\x9F\x9A\x80  Loading Tweets!  \xF0\x9F\x9A\x80')
			response = urllib2.urlopen(turl)
			html = response.read()
			soup = BeautifulSoup(html,'lxml')
	
			tweets = soup.find_all('li','js-stream-item')
			counts=0
			for tweet in tweets:
				if tweet.find('p','tweet-text'):
					try:
						tweet_user = tweet.find('span','username').text
						tweet_text = tweet.find('p','tweet-text').text.encode('utf8')
						tweet_id = tweet['data-item-id']
						timestamp = tweet.find('a','tweet-timestamp')['title']
						bot.sendMessage(chat_id,tweet_text+'\n')
						counts = counts+1
						print counts
						print timetweets
						if counts == int(timetweets):
							break
						else: 
							pass
							time.sleep(1)
						
					except UnicodeDecodeError:
						pass
				else:
					continue
			return 0
		#end twitter search
	
		#coin
		elif command.startswith('coin') or command.startswith('Coin'):
				res = requests.get('https://api.coinsecure.in/v1/exchange/ticker')
				#print(res.text)
				j = json.loads(res.text)
				sell = j['message']['bid']
				bot.sendMessage(chat_id,str(sell)+' INR')
				return 0
		#end coin
	
		#h1 report details
		elif command.startswith('#'):
				repnum=command[1:]
				bot.sendMessage(chat_id,'\xF0\x9F\x9A\x80  Loading report  \xF0\x9F\x9A\x80')
				site = requests.get('https://hackerone.com/reports/'+repnum+'.json')
				json_data = json.loads(site .text)
				if json_data['has_bounty?'] != 0:
					bounty='Bounty: '+json_data['formatted_bounty']
				replink = 'https://hackerone.com/reports/'+repnum
				title = json_data['title']
				username = json_data['reporter']['username']
				url = json_data['reporter']['url']
				state = json_data['readable_substate']
				vulninfo = 'Details:\n'+json_data['vulnerability_information']
				bot.sendMessage(chat_id,parse_mode='HTML',text='(<a href="'+replink+'">#'+repnum+'</a>) <b>'+title+' reported by </b><a href="https://hackerone.com'+url+'">'+username+'</a> <b>('+state+')</b>')
				if json_data['has_bounty?'] != 0:
					bot.sendMessage(chat_id,bounty)
				bot.sendMessage(chat_id,vulninfo)
				print "\n"
				return 0
		#end h1 report details
		
	
		#motivateme
		def motivation():
			turl = "https://twitter.com/search?q=motivation&src=typd&lang=en"
			bot.sendMessage(chat_id,'\xF0\x9F\x9A\x80  Get motivated every one hour!  \xF0\x9F\x9A\x80')
			response = urllib2.urlopen(turl)
			html = response.read()
			soup = BeautifulSoup(html,'lxml')
			tweets = soup.find_all('li','js-stream-item')
			counts=0
			timetweets = "3"
			for tweet in tweets:
				if tweet.find('p','tweet-text'):
					try:
						tweet_user = tweet.find('span','username').text
						tweet_text = tweet.find('p','tweet-text').text.encode('utf8')
						tweet_id = tweet['data-item-id']
						timestamp = tweet.find('a','tweet-timestamp')['title']
						bot.sendMessage(chat_id,tweet_text+'\n')
						counts = counts+1
						if counts == int(timetweets):
							break
						else: 
							pass
							time.sleep(1)
						
					except UnicodeDecodeError:
						pass
				else:
					continue
			print(time.ctime())
			threading.Timer(3600, motivation).start()
	
			if command.startswith('motivateme') or command.startswith('Motivateme'):
				motivation()
				return 0
			else:
				print 'Nothing'
		#end motivation
	
		#youtube search
		if command.startswith('yt') or command.startswith('Yt'):
			param = command[3:]
			response = urlopen("https://www.youtube.com/results?search_query="+param)
			data = response.read()
			response.close()
			soup = BeautifulSoup(data,"html.parser")
			vid = soup.find(attrs={'class':'yt-uix-tile-link'})
			link = "https://www.youtube.com"+vid['href']
			#watchid = vid['href']
			#watchid = watchid.replace('/watch?v=','')
			title = vid['title']
			titleshorten = title[0:12]
			print "Shorten Title is : "+titleshorten
			print title
			#print link
			bot.sendMessage(chat_id,title+"\n"+link)
			#bot.sendMessage(chat_id,'Audio File is on the Way , Wait....\n')
	
			options = {
				'format': 'bestaudio/best',
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '320'
				}]
			}

			with youtube_dl.YoutubeDL(options) as ydl:
				ydl.download([link])

			for i,line in enumerate(os.listdir('.')):
				if titleshorten in line:
					thatline = line
					print 'Thatline: '+thatline
					bot.sendAudio(chat_id,audio=open(thatline,'rb'))
					print "Sent!"
					os.remove(thatline)
		else:
			bot.sendMessage(chat_id,'\xF0\x9F\x98\x88 [+] Got Command \xF0\x9F\x98\x88')
			bot.sendMessage(chat_id,command)
			bot.sendMessage(chat_id,'\xF0\x9F\x92\xBB  [-] Wait.....[-]')
			aa=subprocess.check_output(command,shell=True)
			bot.sendMessage(chat_id,aa)

	
		



#api credentials
api = open('api.txt','r')
api_cont = api.read().strip()
bot = telepot.Bot(api_cont)
bot.message_loop(handle)
print '[+] Server is Listenining [+]'
print '[=] Type Command from Messenger [=]'

while 1:
		time.sleep(10)
