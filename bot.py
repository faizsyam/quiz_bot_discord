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
client = discord.Client()

@bot.event
async def on_ready():
    print('Ready To Go!')

@bot.command(name='kecewa')
async def kecewa(ctx, *args):
    s = ' '.join(args)
    await ctx.send('-play kecewa (' + s + ' mengecewakan)')

@bot.command(name='hello')
async def hello(ctx):
    if isinstance(ctx.channel,discord.DMChannel):
        # response = 'Hello {0.author.mention}'.format(ctx.message)
        # response = 'Your ID is {0.author.id}'.format(ctx.message)
        response = 'ID: ' + str(ctx.author.id)

    else:
        response = 'Pagi bois {0.author.mention}'.format(ctx.message)
    await ctx.send(response)

@bot.command(name='ohno')
async def ohno(ctx):
    if (ctx.author.id in player_ids) & (game_state[0]>=2):
        found = False
        for i,pid in enumerate(player_ids):
            if (pid==ctx.author.id) & (player_lie_streak[i]>=3):
                found = True
                await ctx.send('Oh No no.. NoOOooO! 👿👿')
                break
        if not found:
            await ctx.send('Oh no no noo..')
    else:
        await ctx.send('Oh no no noo..')

@bot.command(name='ohyes')
async def ohyes(ctx):
    if (ctx.author.id in player_ids) & (game_state[0]>=2):
        found = False
        for i,pid in enumerate(player_ids):
            if (pid==ctx.author.id) & (player_streak[i]>=3):
                found = True
                await ctx.send('OWwW YEaAAAH! 🔥🔥🔥')
                break
        if not found:
            await ctx.send('Oh yes yes yess..')
    else:
        await ctx.send('Oh yes yes yess..')

@bot.command(name='ha')
async def ha(ctx):
    response = 'Ha apalagi? {0.author.mention}'.format(ctx.message)
    await ctx.send(response)

@bot.command()
async def dm(ctx):
    await ctx.author.send('Hi! Disini chat kalau mau DM :)')

def background_delay():
    time.sleep(3)

#---------------------------------------------------------------------------------

# Game settings
min_players = 3
round_amount = 3
score_real = 200
score_fake = 100
score_streak = 50
score_lie_streak = 25

max_streak = 10

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
score = []

player_streak = []
player_lie_streak = []
player_answered = []
player_questions = []

all_answered = [False]

#---------------------------------------------------------------------------------

@bot.command(name='cancel')
async def cancel(ctx):
    await ctx.send('Maaf om, belum dibikin cancel nya :) {0.author.mention}'.format(ctx.message))

@bot.command(name='leave')
async def leave(ctx):
    await ctx.send('YOU CAN NEVER LEAVE! {0.author.mention}'.format(ctx.message))
    # if (game_state[0]==1) & 
    #     await ctx.send('YOU CAN NEVER LEAVE! {0.author.mention}'.format(ctx.message))
    #     wait()
    #     response = 'Just kidding. {0.author.mention} '.format(ctx.message)

    #     await ctx.send(response)

@bot.command(name='howto')
async def howto(ctx):
    await ctx.send('nanti kita ganti2an dikasi pertanyaan\nterus harus dijawab jujur\npemain lain juga menjawab kira2 apa yg akan dijawab pemain yang ditanya\nterus nanti ada daftar jawaban\nnah kita harus nebak jawaban mana yang asli\nkalau berhasil jawab yang asli,yang nebak sama pemain yang ditanya dapat poin\nkalau dapat jawaban yang salah, pemain yang bikin jawabannya dapat score')

@bot.command(name='create')
async def play(ctx):
    if game_state[0] != 0:
        await ctx.send('Permainan syudah dibikin boskuu. Silahkan ketik !join untuk bergabung')
    else:
        channel_name[0] = ctx.channel.name
        # guild_name  
        player_ids.clear()
        player_names.clear()
        await ctx.send('**Permainan dimulai!**\n`Silahkan ketik !join untuk bergabung.`')
        game_state[0] = 1

@bot.command(name='join')
async def join(ctx):
    if (game_state[0] == 1) & (not isinstance(ctx.channel,discord.DMChannel)):
        if ctx.author.id not in player_ids:
            player_names.append(ctx.author.mention) # id, mention
            player_ids.append(ctx.author.id)
            await ctx.send(ctx.author.mention + " berhasil join!")
            response = ''
            for i,ply in enumerate(player_names):
                response+='\n' + str(i+1) + ". "
                response+=ply
            embed = discord.Embed(
                title = 'Daftar Pemain:',
                description = response,
                colour = discord.Colour.blue()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send('Maaf ' + ctx.author.mention + ", anda telah join.")

@bot.command(name='start')
async def start(ctx):
    if game_state[0] == 1:
        if len(player_names) < min_players:
            await ctx.send('Maaf bro, jumlah pemain masih kurang. Minimal ' + str(min_players) + ' orang.')
        else :

            round[0] = 1
            player_turn[0] = 0

            await ctx.send('Permainan dimulai!')
            score.clear()
            for ply in player_names:
                score.append(0)

            response = ''
            for j,ply in enumerate(player_names):
                response+='\n' + str(j+1) + ". "
                response+=ply+': '+str(score[j])
            embed = discord.Embed(
                title = 'Score:',
                description = response,
                colour = discord.Colour.blue()
            )
            await ctx.send(embed=embed)

            player_answered.clear()
            player_answers.clear()
            player_questions.clear()
            player_streak.clear()
            player_lie_streak.clear()

            for i in player_names:
                player_questions.append([])
                player_answers.append(-1)
                player_streak.append(0)
                player_lie_streak.append(0)

            game_state[0] = 2

            ply = player_names[player_turn[0]]
            current_player[0] = [player_turn[0],ply]
            await ctx.send("---------------------------------------------------")
            await ctx.send("**Ronde " + str(round[0]) + ":** Pertanyaan untuk "+ ply)
            random_number = random.randrange(len(list_pertanyaan))
            while random_number in player_questions[player_turn[0]]:
                random_number = random.randrange(len(list_pertanyaan))
            player_questions[player_turn[0]].append(random_number)
            pertanyaan = list_pertanyaan[random_number]
            # await ctx.send('**' + pertanyaan + '**')
            embed = discord.Embed(
                title = '**' + pertanyaan + '**',
                colour = discord.Colour.blue()
            )
            await ctx.send(embed=embed)
            await ctx.send('`Ketik !jawab untuk memasukkan jawaban anda.`')

            all_answered[0] = False
                        

@bot.command(name='jawab')
async def jawab(ctx):
    if (game_state[0] == 2) & (ctx.author.id in player_ids):
        await ctx.author.send("Masukkan jawaban anda disini. Awali jawaban dengan !a. (Misalkan: !a Saya suka pisang)") 
    elif (game_state[0] == 3) & (ctx.author.id in player_ids):
        if ctx.author.mention == current_player[0][1]:
            await ctx.author.send("Anda tidak bisa menebak.") 
        else:
            await ctx.author.send("Masukkan tebakan anda disini. Awali jawaban dengan !a, diikiti oleh nomor tebakan. (Misalkan: !a 1)") 
            response = 'Berikut list jawaban:'
            for j,a in enumerate(answers_temp):
                response += '\n`' + str(j+1)+ '`  ' + answers_temp[j][1]
            await ctx.author.send(response)   

@bot.command(name='a') 
async def a(ctx, *jawaban):
    if (game_state[0] == 2) & (ctx.author.id in player_ids):
        if isinstance(ctx.channel,discord.DMChannel):
            for i,id in enumerate(player_ids):
                if id == ctx.author.id:
                    if i not in player_answered:
                        player_answered.append(i)
                    player_answers[i] = ' '.join(jawaban).capitalize()
            await ctx.send('Jawaban diterima.')
            if len(player_answered) == len(player_names):
                game_state[0] = 3
                for guild in bot.guilds:
                    if guild.name == GUILD:
                        for i,text_channel in enumerate(guild.text_channels):
                            if (text_channel.name == channel_name[0]) & (all_answered[0]==False):
                                all_answered[0] = True
                                await guild.text_channels[i].send('Semua pemain telah menjawab.')
                                answers_temp.clear()
                                for a in range(len(player_names)):
                                    if(player_answers[a] != -1):
                                        t = []
                                        t.append(a)
                                        t.append(player_answers[a])
                                        answers_temp.append(t)
                                random.shuffle(answers_temp)
                                response = ''
                                for j,a in enumerate(answers_temp):
                                    response += '\n`' + str(j+1)+ '`  ' + answers_temp[j][1]
                                embed = discord.Embed(
                                    title = 'Mari kita lihat semua jawaban kalian.',
                                    description = response,
                                    colour = discord.Colour.blue()
                                )
                                await guild.text_channels[i].send(embed=embed)   
                                await guild.text_channels[i].send('Silahkan kalian tebak jawaban mana yang merupakan jawabannya ' + current_player[0][1] + '\n`Ketik !jawab untuk menebak.`')
                                all_answered[0] = False
                                player_answered.clear()
                                player_guesses.clear()
                                for i in player_names:
                                    player_guesses.append(-1)
        else:
            response = 'Oh no no. Silahkan masukkan jawaban di DM! {0.author.mention}'.format(ctx.message)
            await ctx.send(response)
    elif (game_state[0] == 3) & (ctx.author.id in player_ids):
        if isinstance(ctx.channel,discord.DMChannel):
            if ctx.author.id == player_ids[current_player[0][0]]:
                await ctx.author.send("Anda tidak bisa menebak.") 
                return 0
            try:
                tebakan = int(jawaban[0])
            except:
                await ctx.send('Tebakan harus angka. Coba lagi.')
                return 0

            if (tebakan < 1) | (tebakan > len(player_answers)):
                await ctx.send('Tebakan di luar jangkauan. Coba lagi.')
                return 0

            for i,id in enumerate(player_ids):
                if id == ctx.author.id:
                    if answers_temp[tebakan-1][0]==i:
                        await ctx.send('Anda tidak bisa memilih jawaban sendiri. Coba lagi.')
                        return 0
                    if i not in player_answered:
                        player_answered.append(i)
                    player_guesses[i] = answers_temp[tebakan-1][0]
            await ctx.send('Tebakan diterima.')
            if len(player_answered) == len(player_names)-1:
                game_state[0] = 4
                for guild in bot.guilds:
                    if guild.name == GUILD:
                        for i,text_channel in enumerate(guild.text_channels):
                            if (text_channel.name == channel_name[0]) & (all_answered[0]==False):
                                all_answered[0] = True
                                await guild.text_channels[i].send('Semua pemain telah memberi tebakan.')
                                await guild.text_channels[i].send('Berikut hasilnya..')
                                jt = -1
                                for j,jwb in enumerate(answers_temp):
                                    if answers_temp[j][0] != current_player[0][0]:
                                        wait()
                                        response = '**Jawaban dari ' + player_names[answers_temp[j][0]] + "**"
                                        response += '\n`' + str(j+1) + '`  ' + answers_temp[j][1]
                                        # await guild.text_channels[i].send(response)
                                        embed = discord.Embed(
                                            description = response,
                                            colour = discord.Colour.red()
                                        )
                                        await guild.text_channels[i].send(embed=embed)
                                        wait()
                                        lost_streak_players = []
                                        response = '> Pemain yang menebak: ['
                                        count = 0
                                        for k,guess in enumerate(player_guesses):
                                            if guess == answers_temp[j][0]:
                                                if count>0:
                                                    response+=', '
                                                response += player_names[k]
                                                if player_streak[k]>=3:
                                                    lost_streak_players.append(k)
                                                player_streak[k]=0
                                                count+=1
                                        response += ']'
                                        lost_streak = False
                                        if count>0:
                                            player_lie_streak[answers_temp[j][0]]+=1
                                        else:
                                            if player_lie_streak[answers_temp[j][0]]>=3:
                                                lost_streak = True
                                            player_lie_streak[answers_temp[j][0]] = 0
                                        score[answers_temp[j][0]] += count*score_fake
                                        await guild.text_channels[i].send(response)
                                        response = 'Score ' + player_names[answers_temp[j][0]] + ' +' + str(count*score_fake)
                                        if player_lie_streak[answers_temp[j][0]] >=3:
                                            score[answers_temp[j][0]] += (player_lie_streak[answers_temp[j][0]]-2)*score_lie_streak
                                            response += ' +' + str((player_lie_streak[answers_temp[j][0]]-2)*score_lie_streak) + ' (lie streak)'
                                        await guild.text_channels[i].send(response)
                                        if lost_streak:
                                            await guild.text_channels[i].send('Ohno ' + player_names[answers_temp[j][0]] + ' kehilangan LYING streak. 🐵')
                                        if player_lie_streak[answers_temp[j][0]] >= 3:
                                            if player_lie_streak[answers_temp[j][0]] == max_streak:
                                                player_lie_streak[answers_temp[j][0]] = 0
                                                await guild.text_channels[i].send('HOLY BEEP! ' + player_names[answers_temp[j][0]] + ' menyelesaikan 10x LYING streak! 🙊😈😈')
                                            else :
                                                await guild.text_channels[i].send('DAMN! ' + player_names[answers_temp[j][0]] + ' is on a ' + str(player_lie_streak[answers_temp[j][0]]) + 'x LYING streak! 🙊')
                                        for k in lost_streak_players:
                                            await guild.text_channels[i].send('Ohno ' + player_names[k] + ' kehilangan winning streak. 😢')
                                    else:
                                        jt = j
                                wait()
                                response = '**Jawaban yang BENAR**\n`'
                                response += str(jt+1) + '`  ' + answers_temp[jt][1]
                                embed = discord.Embed(
                                    description = response,
                                    colour = discord.Colour.green()
                                )
                                await guild.text_channels[i].send(embed=embed)
                                wait()
                                response = '\n> Pemain yang menebak: ['
                                count = 0
                                correct_players = []
                                win_streak_players = []
                                for k,guess in enumerate(player_guesses):
                                    if guess == answers_temp[jt][0]:
                                        if count>0:
                                            response+=', '
                                        response += player_names[k]
                                        correct_players.append(k)
                                        score[k]+=score_real
                                        player_streak[k]+=1
                                        if player_streak[k] >= 3:
                                            score[k]+=score_streak*(player_streak[k]-2)
                                            win_streak_players.append(k)
                                        count+=1
                                response += ']'
                                await guild.text_channels[i].send(response)
                                score[answers_temp[jt][0]] += count*score_real
                                await guild.text_channels[i].send('Score ' + player_names[answers_temp[jt][0]] + ' +' + str(count*score_real))
                                for k in correct_players:
                                    response = 'Score ' + player_names[k] + ' +' + str(score_real)
                                    if k in win_streak_players:
                                        response += ' +' + str(score_streak*(player_streak[k]-2)) + ' (win streak)'
                                    await guild.text_channels[i].send(response)
                                for k in win_streak_players:
                                    if player_streak[k] == max_streak:
                                        await guild.text_channels[i].send('OMG! ' + player_names[k] + ' menyelesaikan 10x winning streak! 🤩🔥🔥🔥')
                                        player_streak[k] = 0
                                    else:
                                        await guild.text_channels[i].send('WOW! ' + player_names[k] + ' is on a ' + str(player_streak[k]) + 'x winning streak! 🤩')

                                wait()
                                response = ''
                                for j,ply in enumerate(player_names):
                                    response+='\n' + str(j+1) + ". "
                                    response+=ply+': '+str(score[j])
                                    if player_streak[j]>=3:
                                        n = player_streak[j]
                                        response += ' '
                                        for k in range(int((n-1)/2)):
                                            response+='🔥'
                                    if player_lie_streak[j]>=3:
                                        n = player_lie_streak[j]
                                        response += ' '
                                        for k in range(int((n-1)/2)):
                                            response+='😈'
                                embed = discord.Embed(
                                    title = 'Score:',
                                    description = response,
                                    colour = discord.Colour.blue()
                                )
                                await guild.text_channels[i].send(embed=embed)

                                player_turn[0]+=1
                                if player_turn[0]>=len(player_names):
                                    player_turn[0] = 0
                                    round[0]+=1
                                    if round[0]>round_amount:
                                        game_state[0] = 0
                                        await guild.text_channels[i].send('Permainan selesai!') # Ranking
                                        scoresorted = score.copy()
                                        scoresorted.sort(reverse=True)
                                        for j in range(len(scoresorted)):
                                            for k in range(len(player_names)):
                                                if score[k] == scoresorted[j]:
                                                    response = ''
                                                    if j<3:
                                                        response += '**'
                                                    response += '#' + str(j+1) + ' ' + player_names[k]
                                                    if j<3:
                                                        response += '**'
                                                        if j==0:
                                                            response+=' 🥇'
                                                        elif j==1:
                                                            response+=' 🥈'
                                                        else:
                                                            response+=' 🥉'
                                                    await guild.text_channels[i].send(response)
                                                    score[k] = -1
                                                    break
                                        return 0
                                # lanjutin ulang kembali ke gs 2
                                game_state[0] = 2
                                player_answered.clear()
                                player_answers.clear()
                                for j in player_names:
                                    player_answers.append(-1)

                                ply = player_names[player_turn[0]]
                                current_player[0] = [player_turn[0],ply]
                                await guild.text_channels[i].send("---------------------------------------------------")
                                await guild.text_channels[i].send("**Ronde " + str(round[0]) + ":** Pertanyaan untuk "+ ply)

                                random_number = random.randrange(len(list_pertanyaan))
                                while random_number in player_questions[player_turn[0]]:
                                    random_number = random.randrange(len(list_pertanyaan))
                                player_questions[player_turn[0]].append(random_number)
                                pertanyaan = list_pertanyaan[random_number]

                                # await guild.text_channels[i].send('**' + pertanyaan + '**')

                                embed = discord.Embed(
                                    title = '**' + pertanyaan + '**',
                                    colour = discord.Colour.blue()
                                )
                                await guild.text_channels[i].send(embed=embed)
                                await guild.text_channels[i].send('`Ketik !jawab untuk memasukkan jawaban anda.`')

                                all_answered[0] = False
        else:
            response = 'Oh no no. Silahkan masukkan tebakan di DM! {0.author.mention}'.format(ctx.message)
            await ctx.send(response)

# @bot.command(name='tebak')
# async def tebak(ctx):
    

def wait():
    thread = threading.Thread(target=background_delay)
    thread.start()
    thread.join()

# @bot.command(name='g')  # cant vote
# async def g(ctx, tebakan: int):
    

@bot.command(name='belum') 
async def belum(ctx):
    if (game_state[0] >= 2) & (game_state[0] <= 3) & (ctx.author.id in player_ids):
        response = 'Pemain yang belum memberi jawaban: ['
        count = 0
        for i in range(len(player_names)):
            flag = (game_state[0]==3) & (i==current_player[0][0])
            if (i not in player_answered) & (not flag):
                if count > 0:
                    response += ', '
                response += player_names[i]
                count+=1
        response+=']'
        await ctx.send(response)

bot.run(TOKEN)