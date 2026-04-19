from core.client import NebulaBot
import uvloop

if __name__ == "__main__":
    uvloop.install()
    bot = NebulaBot()
    bot.run()
