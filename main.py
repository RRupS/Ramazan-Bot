# ----- Imports ----- #
import discord
import os
from dotenv import load_dotenv
from discord.ext import tasks
import datetime
import requests
import pytz
from pytz import timezone
# ------------------- #

intents = discord.Intents.all()
client = discord.Client(intents=intents)

load_dotenv()

token = os.getenv('TOKEN')
test_token = os.getenv('TEST_TOKEN')

@tasks.loop(minutes=1)
async def updateChannels():
    kodlar = {
        'adana': '9146',
        'istanbul': '9541',
        'elazig': '9432'
    }

    aylar = {
        'Ocak': 1,
        'Şubat': 2,
        'Mart': 3,
        'Nisan': 4,
        'Mayıs': 5,
        'Haziran': 6,
        'Temmuz': 7,
        'Ağustos': 8,
        'Eylül': 9,
        'Ekim': 10,
        'Kasım': 11,
        'Aralık': 12
    }

    kanallar = {
        'adana': {
            'ezan': 959955628699312178,
            'kalan': 959955641735204874
        },
        'istanbul': {
            'ezan': 959958731351785532,
            'kalan': 959958743443980298
        },
        'elazig': {
            'ezan': 959960883088457738,
            'kalan': 959960884413878342
        }
    }

    utc_now = datetime.datetime.utcnow()
    utc = pytz.timezone('UTC')
    aware_date = utc.localize(utc_now)
    turkey = timezone('Europe/Istanbul')
    now_turkey = aware_date.astimezone(turkey).replace(tzinfo=None)

    for sehir in kodlar.keys():
        x = requests.get(url='https://namaz-vakti-api.herokuapp.com/data', params={'region': kodlar[sehir]}).json()

        iftar_saati = x[0][5][:-3]
        iftar_dakika = x[0][5][-2:]

        sahur_saati = x[0][1][:-3]
        sahur_dakika = x[0][1][-2:]

        sahur_saati_yarin = x[1][1][:-3]
        sahur_dakika_yarin = x[1][1][-2:]

        y = 0
        z = True

        if now_turkey.hour > int(iftar_saati):
            y = 1
            saat = sahur_saati_yarin+':'+sahur_dakika_yarin
            ezan = 'Sahur'
        elif now_turkey.hour == int(iftar_saati):
            if now_turkey.minute > int(iftar_dakika):
                y = 1
                saat = sahur_saati_yarin+':'+sahur_dakika_yarin
                ezan = 'Sahur'
            elif now_turkey.minute == int(iftar_dakika):
                z = False
                saat = 'İftar Vakti!'
            else:
                saat = iftar_saati+':'+iftar_dakika
                ezan = 'İftar'
        else:
            if now_turkey.hour > int(sahur_saati):
                saat = iftar_saati+':'+iftar_dakika
                ezan = 'İftar'
            elif now_turkey.hour == int(sahur_saati):
                if now_turkey.minute > int(sahur_dakika):
                    saat = iftar_saati+':'+iftar_dakika
                    ezan = 'İftar'
                elif now_turkey.minute == int(sahur_dakika):
                    z = False
                    saat = 'Sahur Vakti!'
                else:
                    saat = sahur_saati+':'+sahur_dakika
                    ezan = 'Sahur'
            else:
                saat = sahur_saati+':'+sahur_dakika
                ezan = 'Sahur'

        tarih = datetime.datetime(int(x[y][0].split()[2]), aylar[x[y][0].split()[1]], int(x[y][0].split()[0]), int(saat.split(':')[0]), int(saat.split(':')[1]), 0, 0)
        kalan_sure = str(tarih-now_turkey).split('.')[0].split(':')[0]+' saat, '+str(tarih-now_turkey).split('.')[0].split(':')[1]+' dakika'

        await client.get_channel(kanallar[sehir]['ezan']).edit(name=ezan+': '+saat)
        if z:
            await client.get_channel(kanallar[sehir]['kalan']).edit(name=kalan_sure)
        else:
            await client.get_channel(kanallar[sehir]['kalan']).edit(name=saat)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='rups development'))
    updateChannels.start()
    print('Bot is ready!')

client.run(token)