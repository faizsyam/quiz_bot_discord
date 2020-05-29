# bot.py
import os
import random
import discord
import threading
import time

from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from game import list_pertanyaan

print('Initializing..')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD') # change to automatically detect

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Ready To Go!')

@bot.command(name='Hello')
async def hello(ctx):
    if isinstance(ctx.channel,discord.DMChannel):
        # response = 'Hello {0.author.mention}'.format(ctx.message)
        # response = 'Your ID is {0.author.id}'.format(ctx.message)
        response = 'ID: ' + str(ctx.author.id)

    else:
        response = 'Selamat pagi. Ha apalagi!? {0.author.mention}'.format(ctx.message)
    await ctx.send(response)


@bot.command()
async def dm(ctx):
    await ctx.author.send('Hi! Disini chat kalau mau DM :)')

def background_delay():
    time.sleep(3)

#---------------------------------------------------------------------------------


# Game settings
min_players = 2
round_amount = 2
score_real = 300
score_fake = 100

game_state = [0]

channel_name = [0]
player_names = []
player_ids = []
player_answers = []
player_guesses = []
current_player = [0]
round = [0]
player_turn = [0]
answers_temp = []
score = []          # scoring when guessing correctly, look at refernce

player_answered = []

#---------------------------------------------------------------------------------

@bot.command(name='create')
async def play(ctx):
    if game_state[0] != 0:
        await ctx.send('Permainan syudah dibikin boskuu. Silahkan ketik !join untuk bergabung')
    else:
        channel_name[0] = ctx.channel.name
        player_ids.clear()
        player_names.clear()
        await ctx.send('Permainan dimulai! Silahkan ketik !join untuk bergabung.')
        game_state[0] = 1

@bot.command(name='join')
async def join(ctx):
    if (game_state[0] == 1) & (not isinstance(ctx.channel,discord.DMChannel)):
        if ctx.author.id not in player_ids:
            player_names.append(ctx.author.mention) # id, mention
            player_ids.append(ctx.author.id)
            await ctx.send(ctx.author.mention + " berhasil join!")
            response = 'Daftar Pemain:'
            for i,ply in enumerate(player_names):
                response+='\n' + str(i+1) + ". "
                response+=ply
            await ctx.send(response)
        else:
            await ctx.send('Maaf ' + ctx.author.mention + ", anda telah join.")

@bot.command(name='start')
async def start(ctx):
    if game_state[0] == 1:
        if len(player_names) < min_players:
            await ctx.send('Maaf bro, jumlah pemain masih kurang. Minimal ' + str(min_players) + ' orang.')
        else :
            game_state[0] = 2

            round[0] = 1
            player_turn[0] = 0

            await ctx.send('Permainan dimulai!')
            score.clear()
            for ply in player_names:
                score.append(0)

            response = 'Score: '
            for i,ply in enumerate(player_names):
                response+='\n' + str(i+1) + ". "
                response+=ply+': '+str(score[i])
            await ctx.send(response)

            player_answered.clear()
            player_answers.clear()
            for i in player_names:
                player_answers.append(-1)

            ply = player_names[player_turn[0]]
            current_player[0] = [player_turn[0],ply]
            await ctx.send('------------------------------------------------')
            await ctx.send("Ronde " + str(round[0]) + ": Pertanyaan untuk "+ ply)
            pertanyaan = list_pertanyaan[random.randrange(len(list_pertanyaan))]
            await ctx.send('**' + pertanyaan + '**')
            await ctx.send('Ketik !jawab untuk memasukkan jawaban anda.')
                        

@bot.command(name='jawab')
async def jawab(ctx):
    if (game_state[0] == 2) & (ctx.author.mention in player_names):
        await ctx.author.send("Masukkan jawaban anda disini. Awali jawaban dengan !a. (Misalkan: !a Saya suka pisang)")      

@bot.command(name='a')  # cant self answer
async def a(ctx, *jawaban):
    if (game_state[0] == 2) & (ctx.author.mention in player_names):
        if isinstance(ctx.channel,discord.DMChannel):
            for i,name in enumerate(player_names):
                if name == ctx.author.mention:
                    if i not in player_answered:
                        player_answered.append(i)
                    player_answers[i] = ' '.join(jawaban)
            await ctx.send('Jawaban diterima.')
            if len(player_answered) == len(player_names):
                game_state[0] = 3
                for guild in bot.guilds:
                    if guild.name == GUILD:
                        for i,text_channel in enumerate(guild.text_channels):
                            if text_channel.name == channel_name[0]:
                                await guild.text_channels[i].send('Semua pemain telah menjawab.')
                                answers_temp.clear()
                                for a in range(len(player_names)):
                                    if(player_answers[a] != -1):
                                        t = []
                                        t.append(a)
                                        t.append(player_answers[a])
                                        answers_temp.append(t)
                                random.shuffle(answers_temp)
                                response = 'Mari kita lihat semua jawaban kalian.'
                                for j,a in enumerate(answers_temp):
                                    response += '\n' + str(j+1)+ '. ' + answers_temp[j][1]
                                await guild.text_channels[i].send(response)       
                                await guild.text_channels[i].send('Silahkan kalian tebak jawaban mana yang merupakan jawabannya ' + current_player[0][1] + '\nKetik !tebak untuk menebak.')
                                player_answered.clear()
                                player_guesses.clear()
                                for i in player_names:
                                    player_guesses.append(-1)
        else:
            response = 'Oh no no. Silahkan masukkan jawaban di DM! {0.author.mention}'.format(ctx.message)
            ctx.send(response)

@bot.command(name='tebak') # filter tebakan jawaban sendiri
async def tebak(ctx):
    if (game_state[0] == 3) & (ctx.author.mention in player_names):
        await ctx.author.send("Masukkan tebakan anda disini. Awali jawaban dengan !g, diikiti oleh nomor tebakan. (Misalkan: !g 1)") 
        response = 'Berikut list jawaban:'
        for j,a in enumerate(answers_temp):
            response += '\n' + str(j+1)+ '. ' + answers_temp[j][1]
        await ctx.author.send(response)

def wait():
    thread = threading.Thread(target=background_delay)
    thread.start()
    thread.join()

@bot.command(name='g')  # cant vote
async def g(ctx, tebakan: int):
    if (game_state[0] == 3) & (ctx.author.mention in player_names):
        if isinstance(ctx.channel,discord.DMChannel):
            if (tebakan < 1) | (tebakan > len(player_answers)):
                await ctx.send('Tebakan di luar jangkauan. Coba lagi.')
                return 0

            for i,name in enumerate(player_names):
                if name == ctx.author.mention:
                    if i not in player_answered:
                        player_answered.append(i)
                    player_guesses[i] = answers_temp[tebakan-1][0]
            await ctx.send('Tebakan diterima.')
            if len(player_answered) == len(player_names):
                game_state[0] = 4
                for guild in bot.guilds:
                    if guild.name == GUILD:
                        for i,text_channel in enumerate(guild.text_channels):
                            if text_channel.name == channel_name[0]:
                                await guild.text_channels[i].send('Semua pemain telah memberi tebakan.')
                                await guild.text_channels[i].send('Berikut hasilnya..')
                                jt = -1
                                for j,jwb in enumerate(answers_temp):
                                    if answers_temp[j][0] != current_player[0][0]:
                                        wait()
                                        response = '**Jawaban dari ' + player_names[answers_temp[j][0]] + "**"
                                        response += '\n' + str(j+1) + '. ' + answers_temp[j][1]
                                        await guild.text_channels[i].send(response)
                                        wait()
                                        response = 'Pemain yang menebak: ['
                                        count = 0
                                        for k,guess in enumerate(player_guesses):
                                            if guess == answers_temp[j][0]:
                                                if count>0:
                                                    response+=', '
                                                response += player_names[k]
                                                count+=1
                                        response += ']'
                                        score[answers_temp[j][0]] += count*score_fake
                                        await guild.text_channels[i].send(response)
                                        await guild.text_channels[i].send('Score ' + player_names[answers_temp[j][0]] + ' +' + str(count*score_fake))
                                    else:
                                        jt = j
                                wait()
                                response = '**Jawaban yang BENAR**\n'
                                response += str(jt+1) + '. ' + answers_temp[jt][1]
                                await guild.text_channels[i].send(response)
                                wait()
                                response = '\nPemain yang menebak: ['
                                count = 0
                                for k,guess in enumerate(player_guesses):
                                    if count>0:
                                        response+=', '
                                    if guess == answers_temp[jt][0]:
                                        response += player_names[k]
                                        count+=1
                                response += ']'
                                score[answers_temp[jt][0]] += count*score_real
                                await guild.text_channels[i].send(response)
                                await guild.text_channels[i].send('Score ' + player_names[answers_temp[jt][0]] + ' +' + str(count*score_real))
                                wait()
                                await guild.text_channels[i].send('------------------------------------------------')
                                response = 'Score: '
                                for j,ply in enumerate(player_names):
                                    response+='\n' + str(j+1) + ". "
                                    response+=ply+': '+str(score[j])
                                await guild.text_channels[i].send(response)

                                player_turn[0]+=1
                                if player_turn[0]>=len(player_names):
                                    player_turn[0] = 0
                                    round[0]+=1
                                    if round[0]>round_amount:
                                        game_state[0] = 0
                                        await guild.text_channels[i].send('Permainan selesai!') # Ranking
                                        return 0
                                # lanjutin ulang kembali ke gs 2
                                game_state[0] = 2
                                player_answered.clear()
                                player_answers.clear()
                                for j in player_names:
                                    player_answers.append(-1)

                                ply = player_names[player_turn[0]]
                                current_player[0] = [player_turn[0],ply]
                                await guild.text_channels[i].send('------------------------------------------------')
                                await guild.text_channels[i].send("Ronde " + str(round[0]) + ": Pertanyaan untuk "+ ply)
                                pertanyaan = list_pertanyaan[random.randrange(len(list_pertanyaan))]
                                await guild.text_channels[i].send('**' + pertanyaan + '**')
                                await guild.text_channels[i].send('Ketik !jawab untuk memasukkan jawaban anda.')
        else:
            response = 'Oh no no. Silahkan masukkan tebakan di DM! {0.author.mention}'.format(ctx.message)
            ctx.send(response)


bot.run(TOKEN)