from dotenv import load_dotenv
import discord

from src.discordBot import DiscordClient, Sender
from src.logger import logger
from src.chatgpt import ChatGPT, DALLE
from src.models import OpenAIModel
from src.memory import Memory
from src.server import keep_alive

load_dotenv()

models = OpenAIModel(api_key='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', model_engine='gpt-3.5-turbo')

memory = Memory(system_message='不要回复超过200个字符，用中文回答，你要帮助人')
chatgpt = ChatGPT(models, memory)
dalle = DALLE(models)


def run():
    client = DiscordClient()
    sender = Sender()

    @client.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        user_id = interaction.user.id
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        receive = chatgpt.get_response(user_id, message)
        await sender.send_message(interaction, message, receive)

    @client.tree.command(name="imagine", description="Generate image from text")
    async def imagine(interaction: discord.Interaction, *, prompt: str):
        if interaction.user == client.user:
            return
        await interaction.response.defer()
        image_url = dalle.generate(prompt)
        await sender.send_image(interaction, prompt, image_url)

    @client.tree.command(name="reset", description="Reset ChatGPT conversation history")
    async def reset(interaction: discord.Interaction):
        user_id = interaction.user.id
        logger.info(f"resetting memory from {user_id}")
        try:
            chatgpt.clean_history(user_id)
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send(f'> Reset ChatGPT conversation history < - <@{user_id}>')
        except Exception as e:
            logger.error(f"Error resetting memory: {e}")
            await interaction.followup.send('> Oops! Something went wrong. <')

    client.run('MTA5NjY3NjI5NDMwNzA5NDU1OA.GcKbYF.6u1ylDjcXNIVHHjvjGbvaKhH9HWj_5zw3l7zXo')


if __name__ == '__main__':
    keep_alive()
    run()
