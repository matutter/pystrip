import asyncio
from io import BytesIO, StringIO
from os import read
from token import COMMENT, NEWLINE
from typing import Generator, List
from tokenize import TokenInfo, generate_tokens, OP, STRING, INDENT


async def remove_comments_and_docstrings(source: str):
  """
  Returns 'source' minus comments and docstrings.
  """
  io_obj = StringIO(source)
  out = ""
  prev_toktype = INDENT
  last_lineno = -1
  last_col = 0
  tok: TokenInfo
  for tok in generate_tokens(io_obj.readline):
    token_type = tok[0]
    token_string = tok[1]
    start_line, start_col = tok[2]
    end_line, end_col = tok[3]
    if start_line > last_lineno:
      last_col = 0
    if start_col > last_col:
      out += (" " * (start_col - last_col))
    if token_type == COMMENT:
      pass
    elif token_type == STRING:
      if prev_toktype != INDENT:
        if prev_toktype != NEWLINE:
          if start_col > 0:
            out += token_string
    else:
      out += token_string
    prev_toktype = token_type
    last_col = end_col
    last_lineno = end_line
  return out

async def process_file(path: str):
  with open(path, 'r') as fd:
    text = await remove_comments_and_docstrings(fd.read())
  with open(path.replace('.py', '.strip.py'), 'w') as fd:
    fd.write(text)

async def main(files: List[str]):
  coros = map(process_file, files)
  await asyncio.gather(*coros)
  return 0

if __name__ == '__main__':
  import sys
  files = sys.argv[1:]
  ret = asyncio.run(main(files))
  exit(ret)
