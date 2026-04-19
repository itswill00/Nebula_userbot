import io
import os
import sys
import time
import asyncio
import traceback
from hydrogram import Client
from hydrogram.types import Message
from core.decorators import on_cmd


async def aexec(code, client, message):
    """Fungsi pembungkus untuk eksekusi kode asinkron (aexec)."""
    # Menyediakan konteks yang kaya untuk eksekusi
    exec_globals = {
        "client": client,
        "c": client,
        "message": message,
        "m": message,
        "reply": message.reply_to_message,
        "r": message.reply_to_message,
        "db": client.db,
        "asyncio": asyncio,
        "os": os,
        "sys": sys,
        "time": time,
        "__builtins__": __builtins__
    }
    
    # Bungkus kode dalam fungsi async
    wrapped_code = "async def __exec(client, message):\n" + "".join(f"    {line}\n" for line in code.split("\n"))
    
    try:
        exec(wrapped_code, exec_globals)
        return await exec_globals["__exec"](client, message)
    except Exception:
        raise


@Client.on_message(on_cmd(["eval", "ev"], category="Developer", info="Eksekusi kode Python secara asinkron."))
async def evaluate_python(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Masukkan kode Python untuk dievaluasi.**")

    code = message.text.split(None, 1)[1]
    status = await client.fast_edit(message, "⚙️ **Evaluating...**")

    # Siapkan penangkapan output
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_stdout = sys.stdout = io.StringIO()
    redirected_stderr = sys.stderr = io.StringIO()
    
    stdout, stderr, exc = None, None, None
    start_time = time.time()

    try:
        value = await aexec(code, client, message)
    except Exception:
        value = None
        exc = traceback.format_exc()

    end_time = time.time()
    stdout = redirected_stdout.getvalue()
    stderr = redirected_stderr.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    # Format Output
    evaluation = exc or stderr or stdout or str(value) if value is not None else "Success (No Output)"
    duration = f"{(end_time - start_time) * 1000:.2f}ms"

    final_output = (
        f"💻 **EVAL**\n\n"
        f"**Code:**\n```python\n{code}```\n\n"
        f"**Output (in {duration}):**\n```python\n{evaluation}```"
    )

    if len(final_output) > 4096:
        # Kirim sebagai file jika terlalu panjang
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval_result.txt"
            await message.reply_document(
                document=out_file, 
                caption=f"📝 **Eval Result** (Too long for message)\n`Time: {duration}`"
            )
            await status.delete()
    else:
        await status.edit(final_output)


@Client.on_message(on_cmd(["bash", "sh"], category="Developer", info="Jalankan perintah terminal (Bash)."))
async def bash_executor(client, message: Message):
    if len(message.command) < 2:
        return await client.fast_edit(message, "⚠️ **Masukkan perintah bash.**")

    cmd = message.text.split(None, 1)[1]
    status = await client.fast_edit(message, f"🐚 **Running:** `{cmd}`")

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    result = (stdout.decode().strip() or "") + (stderr.decode().strip() or "")
    if not result:
        result = "Success (No Output)"

    final_output = f"🐚 **BASH**\n\n**Command:**\n`{cmd}`\n\n**Output:**\n```\n{result}\n```"

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "bash_result.txt"
            await message.reply_document(
                document=out_file,
                caption=f"📝 **Bash Result**\n`Cmd: {cmd}`"
            )
            await status.delete()
    else:
        await status.edit(final_output)
