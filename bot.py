import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@bot.event
async def on_ready():
    print(f'🤖 Bot conectado como {bot.user}')
    print(f'✅ Pronto para dar boas-vindas e responder perguntas!')

@bot.event
async def on_member_join(member):
    """Dá boas-vindas no canal específico"""
    CANAL_BOAS_VINDAS_ID = 1456687223951986760
    canal_boas_vindas = bot.get_channel(CANAL_BOAS_VINDAS_ID)
    
    if canal_boas_vindas:
        embed = discord.Embed(
            title="🎉 Bem-vindo ao servidor!",
            description=f"Olá {member.mention}! Seja muito bem-vindo(a) ao **{member.guild.name}**!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="💡 Dica",
            value="Use o comando `!Pitosga` seguido da sua pergunta para invocar a IA no canal geral!",
            inline=False
        )
        embed.set_image(url="https://cdn.dicionariopopular.com/imagens/numero-seis.gif")
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Você é o membro #{member.guild.member_count}")
        
        await canal_boas_vindas.send(embed=embed)
    else:
        print(f"⚠️ Canal de boas-vindas não encontrado (ID: {CANAL_BOAS_VINDAS_ID})")

@bot.command(name='Pitosga')
async def invocar_ia(ctx, *, pergunta: str = None):
    """Invoca a IA - só funciona no canal geral"""
    CANAL_GERAL_ID = 1456685695790874647
    
    # Verifica se está no canal correto
    if ctx.channel.id != CANAL_GERAL_ID:
        await ctx.send("❌ Este comando só funciona no canal <#1456685695790874647>!")
        return
    
    if not pergunta:
        await ctx.send("🦎 Você precisa fazer uma pergunta! Exemplo: `!Pitosga qual o sentido da vida?`")
        return
    
    async with ctx.typing():
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente amigável em um servidor do Discord. Responda de forma breve, divertida e útil em português."
                    },
                    {
                        "role": "user",
                        "content": pergunta
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000,
            )
            
            resposta = chat_completion.choices[0].message.content
            
            if len(resposta) > 2000:
                chunks = [resposta[i:i+2000] for i in range(0, len(resposta), 2000)]
                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                embed = discord.Embed(
                    title="🦎 Resposta da IA",
                    description=resposta,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Pergunta de {ctx.author.name}")
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Erro ao invocar a IA: {str(e)}")
            print(f"Erro: {e}")

@bot.command(name='ajuda-bot')
async def ajuda(ctx):
    """Mostra os comandos disponíveis"""
    embed = discord.Embed(
        title="📚 Comandos do Bot",
        description="Aqui estão os comandos disponíveis:",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="!Pitosga [pergunta]",
        value="Invoca a IA para responder sua pergunta (só funciona no canal geral)",
        inline=False
    )
    embed.add_field(
        name="!ajuda-bot",
        value="Mostra esta mensagem de ajuda",
        inline=False
    )
    embed.set_footer(text="Bot criado com ❤️ por patitoagiota")
    await ctx.send(embed=embed)

if __name__ == "__main__":
    discord_token = os.getenv("DISCORD_TOKEN")
    
    if not discord_token:
        print("❌ ERRO: Defina suas chaves no arquivo .env")
        print("DISCORD_TOKEN=seu_token")
        print("GROQ_API_KEY=sua_chave")
    else:
        bot.run(discord_token)