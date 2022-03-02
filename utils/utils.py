async def aexec(code, **options):
    final_code = f"""
async def __ex(options):
    for key, value in options.items():
        print(key, value)
        globals()[key] = value
""" +  " "*4 + ("\n" + " " * 4).join(f'{l}' for l in code.split('\n'))

    exec(final_code)
    
    return await locals()['__ex'](options)