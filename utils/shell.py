import asyncio

async def async_exec(cmd: str, timeout: int = 60) -> str:
    """Mengeksekusi perintah shell secara asinkron dengan batas waktu."""
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        
        output = stdout.decode().strip() or stderr.decode().strip()
        if not output:
            return "Command executed successfully with no output."
            
        if len(output) > 4000:
            return output[:4000] + "\n...[Output Truncated]"
            
        return output
    except asyncio.TimeoutError:
        return f"Process timed out after {timeout} seconds."
    except Exception as e:
        return f"Execution error: {str(e)}"
