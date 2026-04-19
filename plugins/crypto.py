import aiohttp
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd

@Client.on_message(on_cmd("crypto", category="Scraper", info="Cek harga crypto (Bitcoin, Ethereum, dll)."))
async def crypto_price(client, message: Message):
    if len(message.command) < 2:
        coin = "bitcoin"
    else:
        coin = message.command[1].lower()

    await client.fast_edit(message, f"⏳ `Mencari harga {coin}...`")
    
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,idr"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if coin in data:
                        usd = data[coin]['usd']
                        idr = data[coin]['idr']
                        text = (
                            f"🪙 **Pasar Crypto: {coin.title()}**\n\n"
                            f"💵 **USD:** `${usd:,.2f}`\n"
                            f"🇮🇩 **IDR:** `Rp {idr:,.2f}`\n\n"
                            f"_(Data dari CoinGecko)_"
                        )
                        await client.fast_edit(message, text)
                    else:
                        await client.fast_edit(message, f"❌ Koin `{coin}` tidak ditemukan di CoinGecko.")
                else:
                    await client.fast_edit(message, "❌ Gagal menyambung ke server harga.")
    except Exception as e:
        await client.fast_edit(message, f"❌ **Error:** `{str(e)}`")
