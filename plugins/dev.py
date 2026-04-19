import io
import sys
import traceback
from hydrogram import Client, filters
from hydrogram.types import Message

PREFIX = "."


@Client.on_message(filters.command("eval", prefixes=PREFIX) & filters.me)
async def evaluate_python(client, message: Message):
    """Menjalankan kode Python secara dinamis (REPL)."""
    if len(message.command) < 2:
        return await message.edit("`Masukkan kode Python.`")

    code = message.text.split(maxsplit=1)[1]
    status = await message.edit("`Evaluating...`")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        # Provide client and message explicitly to the eval context
        exec(
            "async def _eval(client, message):\n" +
            "".join(f"    {line}\n" for line in code.split("\n")),
            globals(),
            locals()
        )
        await locals()["_eval"](client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = f"**Error:**\n```python\n{exc}```\n"
    elif stderr:
        evaluation = f"**Error:**\n```python\n{stderr}```\n"
    elif stdout:
        evaluation = f"**Output:**\n```python\n{stdout}```\n"
    else:
        evaluation = "**Output:**\n`Success with no output.`"

    final_output = f"**Code:**\n```python\n{code}```\n\n{evaluation}"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await message.reply_document(
                document=out_file, caption="`Output terlalu panjang.`"
            )
            await message.delete()
    else:
        await status.edit(final_output)
